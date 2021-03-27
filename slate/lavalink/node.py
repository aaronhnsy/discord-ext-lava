from __future__ import annotations

import asyncio
import logging
from typing import Optional, TYPE_CHECKING

import aiohttp

from slate.bases.node import BaseNode
from slate.objects.stats import LavalinkStats
from slate.utils import ExponentialBackoff

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
            Stats sent from :resource:`lavalink <lavalink>`. These stats are sent every 30 or so seconds. Could be :py:class:`None` if :py:attr:`AndesiteNode.use_compatibility`
            is :py:class:`False`.
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