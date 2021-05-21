from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional, TYPE_CHECKING

import aiohttp
import async_timeout

from slate.exceptions import HTTPError
from slate.bases.node import Node
from slate.objects.stats import AndesiteStats, LavalinkStats, Metadata
from slate.utils import ExponentialBackoff

if TYPE_CHECKING:
    from slate.client import Client


__log__ = logging.getLogger('slate.andesite.node')


class AndesiteNode(Node):
    """
    An implementation of :py:class:`Node` that allows connection to :resource:`andesite <andesite>` nodes with support for their :resource:`lavalink <lavalink>`
    compatible websocket.

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
    use_compatibility: :py:class:`bool`
        Whether or not this node should use the :resource:`lavalink <lavalink>` compatible websocket.
    **kwargs
        Custom keyword arguments that have been passed to this node from :py:meth:`Client.create_node`.
    """

    def __init__(self, *args, use_compatibility: bool = False, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._use_compatibility: bool = use_compatibility

        self._http_url: str = f'http://{self._host}:{self._port}/'
        self._ws_url: str = f'ws://{self._host}:{self._port}/{"websocket" if not self._use_compatibility else ""}'
        self._headers: dict = {
            'Authorization': self._password,
            'User-Id': str(self._client.bot.user.id),
            'Client-Name': 'Slate/0.1.0',
            'Andesite-Short-Errors': 'True'
        }

        self._connection_id: Optional[int] = None
        self._metadata: Optional[Metadata] = None
        self._andesite_stats: Optional[AndesiteStats] = None
        self._lavalink_stats: Optional[LavalinkStats] = None

        self._pong_event = asyncio.Event()

    def __repr__(self) -> str:
        return f'<slate.AndesiteNode is_connected={self.is_connected} is_available={self.is_available} identifier=\'{self._identifier}\' player_count={len(self._players)} ' \
               f'use_compatibility={self._use_compatibility}>'

    #

    @property
    def use_compatibility(self) -> bool:
        """
        :py:class:`bool`:
            Whether or not this node is using the :resource:`lavalink <lavalink>` compatible websocket.
        """
        return self._use_compatibility

    #

    @property
    def connection_id(self) -> Optional[int]:
        """
        Optional [ :py:class:`int` ]:
            The connection id sent upon successful connection with :resource:`andesite <andesite>`. This could be :py:class:`None` if
            :py:attr:`AndesiteNode.use_compatibility` is :py:class:`True`.
        """
        return self._connection_id

    @property
    def metadata(self) -> Optional[Metadata]:
        """
        Optional [ :py:class:`Metadata` ]:
            Metadata sent from :resource:`andesite <andesite>` that contains version information and node information. This could be :py:class:`None` if
            :py:attr:`AndesiteNode.use_compatibility` is :py:class:`True`.
        """
        return self._metadata

    @property
    def andesite_stats(self) -> Optional[AndesiteStats]:
        """
        Optional [ :py:class:`AndesiteStats` ]:
            Stats sent from :resource:`andesite <andesite>` that contains information about the system and current status. These stats are set by using
            :py:meth:`AndesiteNode.request_andesite_stats`.
        """
        return self._andesite_stats

    @property
    def lavalink_stats(self) -> Optional[LavalinkStats]:
        """
        Optional [ :py:class:`LavalinkStats` ]:
            Stats sent from :resource:`andesite <andesite>` when using the :resource:`lavalink <lavalink>` compatible websocket. These stats are set every 30~ seconds using the
            lavalink compatible websocket, or by using :py:meth:`AndesiteNode.request_lavalink_stats`
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
                __log__.warning(f'WEBSOCKET | \'{self.identifier}\'s websocket is disconnected, sleeping for {round(retry)} seconds.')
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

        if op == 'metadata':
            self._metadata = Metadata(data=message.get('data'))

        elif op == 'connection-id':
            self._connection_id = message.get('id')

        elif op == 'pong':
            self._pong_event.set()

        elif op in ['player-update', 'playerUpdate']:

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

            if stats := message.get('stats'):
                self._andesite_stats = AndesiteStats(data=stats)
            else:
                self._lavalink_stats = LavalinkStats(data=message)

    #

    async def ping(self) -> float:
        """
        Returns the latency between this node and it's websocket server in milliseconds.

        Returns
        -------
        :py:class:`float`
            The latency, in milliseconds.

        Raises
        ------
        :py:class:`asyncio.TimeoutError`
            Requesting the latency took over 30 seconds.
        """

        start_time = time.time()
        await self._send(op='ping')

        async with async_timeout.timeout(timeout=30):
            await self._pong_event.wait()

        end_time = time.time()
        self._pong_event.clear()

        return end_time - start_time

    async def request_andesite_stats(self, retry: bool = False, tries: int = 3, raw: bool = False) -> AndesiteStats:
        """
        Requests :resource:`andesite <andesite>` stats from the node.

        Parameters
        ----------
        retry: Optional [ :py:class:`bool` ]
            Whether or not to retry the operation if a non-200 status code is received.
        tries: Optional [ :py:class:`int` ]
            The amount of times to retry the operation if a non-200 status code is received. Defaults to 3.
        raw: Optional [ :py:class:`bool` ]
            Whether or not to return the raw result of the operation.

        Returns
        -------
        :py:class:`AndesiteStats`
            The andesite stats that were returned.

        Raises
        ------
        :py:class:`HTTPError`:
            There was a non-200 status code while fetching the stats.
        """

        backoff = ExponentialBackoff()

        for _ in range(tries):

            async with self.client.session.get(url=f'{self._http_url}/stats', headers={'Authorization': self.password}) as response:

                if response.status != 200:

                    if retry:
                        retry_time = backoff.delay()
                        __log__.warning(f'ANDESITE-STATS | Non-200 status code while fetching andesite stats. Retrying in {round(retry_time)}s. | Status code: {response.status}')
                        await asyncio.sleep(retry_time)
                        continue

                    __log__.error(f'ANDESITE-STATS | Non-200 status code while fetching andesite stats. Not retrying. | Status code: {response.status}')
                    raise HTTPError('Non-200 status code while fetching andesite stats.', status_code=response.status)

                data = await response.json()

            if raw:
                return data

            self._andesite_stats = AndesiteStats(dict(data))
            return self._andesite_stats

        __log__.error(f'ANDESITE-STATS | Non-200 status code while fetching andesite stats. All {tries} retries used. | Status code: {response.status}')
        raise HTTPError(f'Non-200 status code fetching andesite stats. All {tries} retries used.', status_code=response.status)

    async def request_lavalink_stats(self, retry: bool = False, tries: int = 3, raw: bool = False) -> LavalinkStats:
        """
        Requests :resource:`lavalink <lavalink>` stats from the node.

        Parameters
        ----------
        retry: Optional [ :py:class:`bool` ]
            Whether or not to retry the operation if a non-200 status code is received.
        tries: Optional [ :py:class:`int` ]
            The amount of times to retry the operation if a non-200 status code is received. Defaults to 3.
        raw: Optional [ :py:class:`bool` ]
            Whether or not to return the raw result of the operation.

        Returns
        -------
        :py:class:`LavalinkStats`
            The lavalink stats that were returned.

        Raises
        ------
        :py:class:`HTTPError`:
            There was a non-200 status code while fetching the stats.
        """

        backoff = ExponentialBackoff()

        for _ in range(tries):

            async with self.client.session.get(url=f'{self._http_url}/stats/lavalink', headers={'Authorization': self.password}) as response:

                if response.status != 200:

                    if retry:
                        retry_time = backoff.delay()
                        __log__.warning(f'LAVALINK-STATS | Non-200 status code while fetching lavalink stats. Retrying in {round(retry_time)}s. | Status code: {response.status}')
                        await asyncio.sleep(retry_time)
                        continue

                    __log__.error(f'LAVALINK-STATS | Non-200 status code while fetching lavalink stats. Not retrying. | Status code: {response.status}')
                    raise HTTPError('Non-200 status code while fetching lavalink stats.', status_code=response.status)

                data = await response.json()

            if raw:
                return data

            self._lavalink_stats = LavalinkStats(dict(data))
            return self._lavalink_stats

        __log__.error(f'LAVALINK-STATS | Non-200 status code while fetching lavalink stats. All {tries} retries used. | Status code: {response.status}')
        raise HTTPError(f'Non-200 status code fetching lavalink stats. All {tries} retries used.', status_code=response.status)
