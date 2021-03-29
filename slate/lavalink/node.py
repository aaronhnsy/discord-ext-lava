from __future__ import annotations

import asyncio
import logging
from typing import Optional, TYPE_CHECKING

import aiohttp

from slate.bases.node import BaseNode
from slate.objects.stats import LavalinkStats
from slate.utils import ExponentialBackoff
from slate.objects.routeplanner import RoutePlannerStatus
from slate.exceptions import HTTPError

if TYPE_CHECKING:
    from slate.client import Client


__log__ = logging.getLogger('slate.lavalink.node')
__all__ = ['LavalinkNode']


class LavalinkNode(BaseNode):
    """
    An implementation of :py:class:`BaseNode` that allows connection to :resource:`lavalink <lavalink>` nodes.

    Parameters
    ----------
    client: :py:class:`Client`
        The slate client that this node is associated with.
    host: :py:class:`str`
        The host address of the node's websocket.
    port: :py:class:`str`
        The port to connect to the node's websocket with.
    password: :py:class:`str`
        The password used for authentification with the node's websocket and HTTP connections.
    identifier: :py:class:`str`
        This node's unique identifier.
    **kwargs
        Custom keyword arguments that have been passed to this node from :py:meth:`Client.create_node`.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._http_url: str = f'http://{self._host}:{self._port}/'
        self._ws_url: str = f'ws://{self._host}:{self._port}/'
        self._headers: dict = {
            'Authorization': self._password,
            'User-Id': str(self._client.bot.user.id),
            'Client-Name': 'Slate/0.1.0',
        }

        self._lavalink_stats: Optional[LavalinkStats] = None

    def __repr__(self) -> str:
        return f'<slate.AndesiteNode is_connected={self.is_connected} is_available={self.is_available} identifier=\'{self._identifier}\' player_count={len(self._players)}>'

    #

    @property
    def lavalink_stats(self) -> Optional[LavalinkStats]:
        """
        Optional [ :py:class:`LavalinkStats` ]:
            Stats sent from :resource:`lavalink <lavalink>`. Sent every 30 or so seconds.
        """
        return self._lavalink_stats

    #

    async def _listen(self) -> None:

        backoff = ExponentialBackoff(base=7)

        while True:

            message = await self._websocket.receive()

            if message.type is aiohttp.WSMsgType.CLOSED:

                self._available = False

                for player in self._players.copy().values():
                    await player.destroy()

                retry = backoff.delay()
                __log__.warning(f'WEBSOCKET | \'{self.identifier}\'s websocket is disconnected, sleeping for {round(retry, 2)} seconds.')
                await asyncio.sleep(retry)

                if not self.is_connected:
                    __log__.warning(f'WEBSOCKET | \'{self.identifier}\'s websocket is disconnected, attempting reconnection.')
                    self.client.bot.loop.create_task(self._reconnect())

            else:

                message = message.json()

                op = message.get('op', None)
                if not op:
                    __log__.warning(f'WEBSOCKET | \'{self.identifier}\' received payload with no op code. | Payload: {message}')
                    continue

                __log__.debug(f'WEBSOCKET | \'{self.identifier}\' received payload with op \'{op}\'. | Payload: {message}')
                await self.client.bot.loop.create_task(self._handle_message(message=message))

    async def _handle_message(self, message: dict) -> None:

        op = message['op']

        if op == 'playerUpdate':

            player = self.players.get(int(message.get('guildId')))
            if not player:
                return

            await player._update_state(state=message.get('state'))

        elif op == 'event':

            player = self.players.get(int(message.get('guildId')))
            if not player:
                return

            player._dispatch_event(data=message)

        elif op == 'stats':
            self._lavalink_stats = LavalinkStats(data=message)

    #

    async def route_planner_status(self) -> Optional[RoutePlannerStatus]:
        """
        Fetches the route planner status.

        Returns
        -------
        Optional [ :py:class:`RoutePlannerStatus` ]:
            The route planner status object. Could be None if a route planner has not been configured on :resource:`lavalink <lavalink>`.

        Raises
        ------
        :py:class:`HTTPError`:
            There was a non-200 status code while fetching the route planner status.
        """

        async with self.client.session.get(url=f'{self._http_url}/routeplanner/status', headers={'Authorization': self.password}) as response:

            if response.status != 200:
                __log__.error(f'ROUTEPLANNER | Non-200 status code while fetching route planner status. | Status code: {response.status}')
                raise HTTPError('Non-200 status code while fetching route planner status.', status_code=response.status)

            data = await response.json()

        if not data.get('class'):
            return None

        return RoutePlannerStatus(data=dict(data))

    async def route_planner_free_address(self, address: str) -> None:
        """
        Frees a route planner address.

        Parameters
        ----------
        address: str
            The address to free. An example is '1.0.0.1' or something similar.

        Raises
        ------
        :py:class:`HTTPError`:
            There was a non-204 status code while freeing the address.
        """

        async with self.client.session.post(url=f'{self._http_url}/routeplanner/free/address', headers={'Authorization': self.password}, data={'address': address}) as response:

            if response.status != 204:
                __log__.error(f'ROUTEPLANNER | Non-204 status code while freeing route planner address. | Status code: {response.status}')
                raise HTTPError('Non-204 status code while freeing route planner address.', status_code=response.status)

    async def route_planner_free_all_addresses(self) -> None:
        """
        Frees all route planner addresses.

        Raises
        ------
        :py:class:`HTTPError`:
            There was a non-204 status code while freeing the addresses.
        """

        async with self.client.session.post(url=f'{self._http_url}/routeplanner/free/all', headers={'Authorization': self.password}) as response:

            if response.status != 204:
                __log__.error(f'ROUTEPLANNER | Non-204 status code while freeing route planner addresses | Status code: {response.status}')
                raise HTTPError('Non-204 status code while freeing route planner addresses.', status_code=response.status)
