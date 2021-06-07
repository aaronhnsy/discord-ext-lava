from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, List, Optional, TypeVar, Union

import aiohttp

from .objects.enums import Op
from .objects.exceptions import HTTPError, TrackLoadError
from .objects.playlist import ObsidianPlaylist
from .objects.stats import ObsidianStats
from .objects.track import ObsidianTrack
from .player import ObsidianPlayer
from ..client import Client
from ..exceptions import NodeConnectionClosed, NodeConnectionError
from ..utils import ExponentialBackoff


PlayerType = TypeVar('PlayerType', bound=ObsidianPlayer)


__log__ = logging.getLogger('slate.obsidian.node')


class ObsidianNode:

    def __init__(self, *, client: Client, host: str, port: str, password: str, identifier: str) -> None:

        self._client: Client = client
        self._host: str = host
        self._port: str = port
        self._password: str = password
        self._identifier: str = identifier

        self._players: Dict[int, PlayerType] = {}

        self._http_url: str = f'http://{self._host}:{self._port}/'
        self._ws_url: str = f'ws://{self._host}:{self._port}/magma'

        self._headers: dict = {
            'Authorization': self._password,
            'User-Id': str(self._client.bot.user.id),
            'Client-Name': 'Slate/0.1.0',
        }

        self._stats: Optional[ObsidianStats] = None

        self._websocket: Optional[aiohttp.ClientWebSocketResponse] = None
        self._task: Optional[asyncio.Task] = None

        self._available: bool = False

    def __repr__(self) -> str:
        return f'<slate.ObsidianNode is_connected={self.is_connected} is_available={self.is_available} identifier=\'{self._identifier}\' player_count={len(self._players)}>'

    #

    @property
    def client(self) -> Client:
        """
        :py:class:`Client`:
            The slate client that this node is associated with.
        """
        return self._client

    @property
    def host(self) -> str:
        """
        :py:class:`str`:
            The host address of the node's websocket.
        """
        return self._host

    @property
    def port(self) -> str:
        """
        :py:class:`str`:
            The port to connect to the node's websocket with.
        """
        return self._port

    @property
    def password(self) -> str:
        """
        :py:class:`str`:
            The password used for authentification with the node's websocket and HTTP connections.
        """
        return self._password

    @property
    def identifier(self) -> str:
        """
        :py:class:`str`:
            This nodes unique identifier.
        """
        return self._identifier

    #

    @property
    def players(self) -> Dict[int, PlayerType]:
        """
        :py:class:`Dict` [ :py:class:`int` , :py:class:`Player` ]:
            A mapping of player guild id's to players that this node is managing.
        """
        return self._players

    #

    @property
    def is_connected(self) -> bool:
        """
        :py:class:`bool`:
            Whether or not this node is connected to it's websocket.
        """
        return self._websocket is not None and not self._websocket.closed

    @property
    def is_available(self) -> bool:
        """
        :py:class:`bool`:
            Whether or not this node is connected to it's websocket and is available for use.
        """
        return self.is_connected and self._available

    #

    @property
    def stats(self) -> Optional[ObsidianStats]:
        return self._stats

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

                data = message.json()

                try:
                    op = Op(data.get('op', None))
                except ValueError:
                    __log__.warning(f'WEBSOCKET | \'{self.identifier}\' received payload with invalid/missing op code. | Payload: {data}')
                    continue

                else:
                    __log__.debug(f'WEBSOCKET | \'{self.identifier}\' received payload with op \'{op}\'. | Payload: {data}')
                    await self.client.bot.loop.create_task(self._handle_message(op=op, data=data.get('d')))

    async def _handle_message(self, op: Op, data: dict) -> None:

        if op is Op.PLAYER_UPDATE:

            if not (player := self.players.get(int(data.get('guild_id')))):
                return

            await player._update_state(data)

        elif op is Op.PLAYER_EVENT:

            if not (player := self.players.get(int(data.get('guild_id')))):
                return

            player._dispatch_event(data)

        elif op is Op.STATS:
            self._stats = ObsidianStats(data)

    #

    async def _send(self, op: Op, **data) -> None:

        if not self.is_connected:
            raise NodeConnectionClosed(f'Node \'{self.identifier}\' is not connected.')

        data = {'op': op.value, 'd': data}

        await self._websocket.send_json(data)
        __log__.debug(f'WEBSOCKET | Node \'{self.identifier}\' sent a \'{op}\' payload. | Payload: {data}')

    async def _reconnect(self) -> None:

        await self.client.bot.wait_until_ready()

        try:
            websocket = await self.client.session.ws_connect(self._ws_url, headers=self._headers)

        except Exception as error:

            self._available = False

            if isinstance(error, aiohttp.WSServerHandshakeError) and error.status in (401, 4001):
                __log__.warning(f'NODE | \'{self.identifier}\' failed to connect due to invalid authorization.')
            else:
                __log__.warning(f'NODE | \'{self.identifier}\' failed to connect. Error: {error}')

        else:

            self._available = True
            self._websocket = websocket

            if not self._task:
                self._task = asyncio.create_task(self._listen())

            self._client.nodes[self.identifier] = self
            __log__.info(f'NODE | \'{self.identifier}\' connected successfully.')

    #

    async def connect(self) -> None:
        """Connects this node to it's websocket.

        Raises
        ------
        :py:class:`NodeConnectionError`:
            There was an error while connecting to the websocket, could be invalid authorization or an unreachable/invalid host address or port, etc.
        """

        await self.client.bot.wait_until_ready()

        try:
            websocket = await self.client.session.ws_connect(self._ws_url, headers=self._headers)

        except Exception as error:

            self._available = False

            if isinstance(error, aiohttp.WSServerHandshakeError) and error.status in (401, 4001):
                __log__.warning(f'NODE | \'{self.identifier}\' failed to connect due to invalid authorization.')
                raise NodeConnectionError(f'Node \'{self.identifier}\' failed to connect due to invalid authorization.')

            __log__.warning(f'NODE | \'{self.identifier}\' failed to connect. Error: {error}')
            raise NodeConnectionError(f'Node \'{self.identifier}\' failed to connect.\n{error}')

        else:

            self._available = True
            self._websocket = websocket

            if not self._task:
                self._task = asyncio.create_task(self._listen())

            self._client.nodes[self.identifier] = self
            __log__.info(f'NODE | \'{self.identifier}\' connected successfully.')

    async def disconnect(self, *, force: bool = False) -> None:
        """
        Destroys this node's players and disconnects it from it's websocket.

        Parameters
        ----------
        force: :py:class:`bool`
            Whether or not to force disconnection of players.
        """

        for player in self._players.copy().values():
            await player.destroy(force=force)

        if self.is_connected:
            await self._websocket.close()
        self._websocket = None

        self._task.cancel()
        self._task = None

        __log__.info(f'NODE | \'{self.identifier}\' has been disconnected.')

    async def destroy(self, *, force: bool = False) -> None:
        """
        Calls :py:meth:`Node.disconnect` and removes this node from it's client.

        Parameters
        ----------
        force: :py:class:`bool`
            Whether or not to force disconnection of players.
        """

        await self.disconnect(force=force)
        del self._client.nodes[self.identifier]

        __log__.info(f'NODE | \'{self.identifier}\' has been destroyed.')

    #


    async def search(self, query: str, *, ctx: ContextType = None, retry: bool = True, tries: int = 3, raw: bool = False) -> Optional[Union[ObsidianPlaylist, List[ObsidianTrack], Dict]]:

        backoff = ExponentialBackoff()

        for _ in range(tries):

            async with self.client.session.get(url=f'{self._http_url}/loadtracks', headers={'Authorization': self.password}, params={'identifier': query}) as response:

                if response.status != 200:

                    if retry:
                        time = backoff.delay()
                        __log__.warning(f'LOADTRACKS | Non-200 status code while loading tracks. Retrying in {round(time)}s. | Status code: {response.status}')
                        await asyncio.sleep(time)
                        continue

                    __log__.error(f'LOADTRACKS | Non-200 status code while loading tracks. Not retrying. | Status code: {response.status}')
                    raise HTTPError('Non-200 status code while loading tracks.', status_code=response.status)

                data = await response.json()

            if raw:
                return data

            load_type = data.get('load_type')

            if load_type == 'NO_MATCHES':
                __log__.info(f'LOADTRACKS | NO_MATCHES for query: {query} | Data: {data}')
                return None

            if load_type == 'LOAD_FAILED':
                __log__.warning(f'LOADTRACKS | LOAD_FAILED for query: {query} | Data: {data}')
                raise TrackLoadError(data=data.get('exception'))

            if load_type == 'PLAYLIST_LOADED':

                playlist_info = data.get('playlist_info')
                playlist_info['uri'] = query

                __log__.info(f'LOADTRACKS | PLAYLIST_LOADED for query: {query} | Data: {data}')
                return ObsidianPlaylist(playlist_info=playlist_info, tracks=data.get('tracks'), ctx=ctx)

            if load_type in ['SEARCH_RESULT', 'TRACK_LOADED']:
                __log__.info(f'LOADTRACKS | SEARCH_RESULT/TRACK_LOADED for query: {query} | Data: {data}')
                return [ObsidianTrack(track_id=track.get('track'), track_info=track.get('info'), ctx=ctx) for track in data.get('tracks')]

        __log__.error(f'LOADTRACKS | Non-200 status code while loading tracks. All {tries} retries used. | Status code: {response.status}')
        raise HTTPError(f'Non-200 status code while loading tracks. All {tries} retries used.', status_code=response.status)


    async def decode_track(self, track_id: str, *, ctx: ContextType = None, retry: bool = True, tries: int = 3, raw: bool = False) -> Optional[Union[ObsidianTrack, Dict]]:

        backoff = ExponentialBackoff()

        for _ in range(tries):

            async with self.client.session.get(url=f'{self._http_url}/decodetrack', headers={'Authorization': self.password}, params={'track': track_id}) as response:

                if response.status != 200:

                    if retry:
                        time = backoff.delay()
                        __log__.warning(f'DECODETRACK | Non-200 status code while decoding track. Retrying in {round(time)}s. | Status code: {response.status}')
                        await asyncio.sleep(time)
                        continue

                    __log__.error(f'DECODETRACK | Non-200 status code while decoding track. Not retrying. | Status code: {response.status}')
                    raise HTTPError('Non-200 status code while decoding track.', status_code=response.status)

                data = await response.json()

            if raw:
                return data

            return ObsidianTrack(track_id=track_id, track_info=data.get('info', None) or data, ctx=ctx)

        __log__.error(f'DECODETRACK | Non-200 status code while decoding track. All {tries} retries used. | Status code: {response.status}')
        raise HTTPError(f'Non-200 status code while decoding track. All {tries} retries used.', status_code=response.status)

    async def decode_tracks(self, track_ids: List[str], *, ctx: ContextType = None, retry: bool = True, tries: int = 3,  raw: bool = False) -> Optional[Union[List[ObsidianTrack], Dict]]:

        backoff = ExponentialBackoff()

        for _ in range(tries):

            async with self.client.session.post(url=f'{self._http_url}/decodetracks', headers={'Authorization': self.password}, data=json.dumps(track_ids)) as response:

                if response.status != 200:

                    if retry:
                        time = backoff.delay()
                        __log__.warning(f'DECODETRACKS | Non-200 status code while decoding tracks. Retrying in {round(time)}s. | Status code: {response.status}')
                        await asyncio.sleep(time)
                        continue

                    __log__.error(f'DECODETRACKS | Non-200 status code while decoding tracks. Not retrying. | Status code: {response.status}')
                    raise HTTPError('Non-200 status code while decoding tracks.', status_code=response.status)

                data = await response.json()

            if raw:
                return data

            return [ObsidianTrack(track_id=track.get('track'), track_info=track.get('info'), ctx=ctx) for track in data]

        __log__.error(f'DECODETRACKS | Non-200 status code while decoding tracks. All {tries} retries used. | Status code: {response.status}')
        raise HTTPError(f'Non-200 status code while decoding tracks. All {tries} retries used.', status_code=response.status)
