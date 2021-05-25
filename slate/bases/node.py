from __future__ import annotations

import abc
import asyncio
import json
import logging
from typing import Dict, List, Optional, TYPE_CHECKING, Union

import aiohttp
from discord.ext import commands

from slate.exceptions import HTTPError, NodeConnectionClosed, NodeConnectionError, TrackLoadFailed
from slate.objects.playlist import Playlist
from slate.objects.track import Track
from slate.utils import ExponentialBackoff


if TYPE_CHECKING:
    from slate.client import Client
    from slate import PlayerType, ContextType


__all__ = ['Node']
__log__ = logging.getLogger('slate.bases.node')


class Node(abc.ABC):
    """
    The abstract base class for creating a node with. Nodes connect to a websocket such as :resource:`andesite <andesite>` or :resource:`lavalink <lavalink>`
    using custom logic defined in that nodes subclass. All nodes passed to :py:meth:`Client.create_node` must inherit from this class.

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
        This nodes unique identifier.
    **kwargs
        Custom keyword arguments that have been passed to this node from :py:meth:`Client.create_node`
    """

    def __init__(self, *, client: Client, host: str, port: str, password: str, identifier: str, **kwargs) -> None:

        self._client: Client = client
        self._host: str = host
        self._port: str = port
        self._password: str = password
        self._identifier: str = identifier

        self._players: Dict[int, PlayerType] = {}

        self._http_url: Optional[str] = None
        self._ws_url: Optional[str] = None
        self._headers: Optional[Dict[str]] = {}

        self._websocket: Optional[aiohttp.ClientWebSocketResponse] = None

        self._task: Optional[asyncio.Task] = None

        self._available: bool = False

    def __repr__(self) -> str:
        return f'<slate.Node is_connected={self.is_connected} is_available={self.is_available} identifier=\'{self._identifier}\' player_count={len(self._players)}>'

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

    @abc.abstractmethod
    async def _listen(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def _handle_message(self, message: dict) -> None:
        raise NotImplementedError

    #

    async def _send(self, **data) -> None:

        if not self.is_connected:
            raise NodeConnectionClosed(f'Node \'{self.identifier}\' is not connected.')

        __log__.debug(f'WEBSOCKET | Node \'{self.identifier}\' sent a \'{data.get("op")}\' payload. | Payload: {data}')
        await self._websocket.send_json(data)

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

    async def search(self, query: str, *, ctx: ContextType = None, retry: bool = True, tries: int = 3,
                     raw: bool = False) -> Optional[Union[Playlist, List[Track], Dict]]:
        """
        Searches for and returns a list of :py:class:`Track`'s or a :py:class:`Playlist`.

        Parameters
        ----------
        query: str
            The query to search with. Could be a link or a search term if prepended with 'scsearch:' (Soundcloud), 'ytsearch:' (Youtube) or 'ytmsearch: ' (Youtube music).
        ctx: :py:class:`commands.Context`
            An optional discord.py context argument to pass to the result for quality of life features such as :py:attr:`Track.requester`.
        retry: Optional [ :py:class:`bool` ]
            Whether or not to retry the operation if a non-200 status code is received.
        tries: Optional [ :py:class:`int` ]
            The amount of times to retry the operation if a non-200 status code is received. Defaults to 3.
        raw: Optional [ :py:class:`bool` ]
            Whether or not to return the raw result of the operation.

        Returns
        -------
        Optional [ :py:class:`Union` [ :py:class:`Playlist` , :py:class:`List` [ :py:class:`Track` ] , :py:class:`dict` ] ]:
            The raw result, list of tracks, or playlist that was found.

        Raises
        ------
        :py:class:`HTTPError`:
            There was a non-200 status code while searching.
        :py:class:`TrackLoadFailed`:
            The server did not error, but there was some kind of other problem while loading tracks. Could be a restricted video, youtube ratelimit, etc.
        """

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

            load_type = data.pop('loadType')

            if load_type == 'NO_MATCHES':
                __log__.debug(f'LOADTRACKS | No matches found for query: {query}')
                return None

            if load_type == 'LOAD_FAILED':
                __log__.warning(f'LOADTRACKS | Encountered a LOAD_FAILED while getting tracks for query: {query} | Data: {data}')
                raise TrackLoadFailed(data=data)

            if load_type == 'PLAYLIST_LOADED':
                __log__.debug(f'LOADTRACKS | Playlist loaded for query: {query} | Name: {data.get("playlistInfo", {}).get("name", "UNKNOWN")}')
                return Playlist(playlist_info=data.get('playlistInfo'), tracks=data.get('tracks'), ctx=ctx)

            if load_type in ['SEARCH_RESULT', 'TRACK_LOADED']:
                __log__.debug(f'LOADTRACKS | Tracks loaded for query: {query} | Amount: {len(data.get("tracks"))}')
                return [Track(track_id=track.get('track'), track_info=track.get('info'), ctx=ctx) for track in data.get('tracks')]

        __log__.error(f'LOADTRACKS | Non-200 status code while loading tracks. All {tries} retries used. | Status code: {response.status}')
        raise HTTPError(f'Non-200 status code while loading tracks. All {tries} retries used.', status_code=response.status)

    async def decode_track(self, track_id: str, *, ctx: ContextType = None, retry: bool = True, tries: int = 3,
                           raw: bool = False) -> Optional[Union[Track, Dict]]:
        """
        Returns a track object based on its track id.

        Parameters
        ----------
        track_id: str
            The track id to decode.
        ctx: Optional[ :py:class:`commands.Context` ]:
            An optional discord.py context argument to pass to the result for quality of life features such as :py:attr:`Track.requester`.
        retry: Optional [ :py:class:`bool` ]
            Whether or not to retry the operation if a non-200 status code is received.
        tries: Optional [ :py:class:`int` ]
            The amount of times to retry the operation if a non-200 status code is received. Defaults to 3.
        raw: Optional [ :py:class:`bool` ]
            Whether or not to return the raw result of the operation.

        Returns
        -------
        Optional [ :py:class:`Union` [ :py:class:`Track` , :py:class:`dict` ] ]:
            The raw result or track that was returned.

        Raises
        ------
        :py:class:`HTTPError`:
            There was a non-200 status code while decoding tracks.
        """

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

            return Track(track_id=track_id, track_info=data.get('info', None) or data, ctx=ctx)

        __log__.error(f'DECODETRACK | Non-200 status code while decoding track. All {tries} retries used. | Status code: {response.status}')
        raise HTTPError(f'Non-200 status code while decoding track. All {tries} retries used.', status_code=response.status)

    async def decode_tracks(self, track_ids: List[str], *, ctx: ContextType = None, retry: bool = True, tries: int = 3,
                            raw: bool = False) -> Optional[Union[List[Track], Dict]]:
        """
        Returns track objects based on their track ids.

        Parameters
        ----------
        track_ids: :py:class:`List` [ :py:class:`str` ]
            A list of track id's to decode.
        ctx: Optional[ :py:class:`commands.Context` ]:
            An optional discord.py context argument to pass to the result for quality of life features such as :py:attr:`Track.requester`.
        retry: Optional [ :py:class:`bool` ]
            Whether or not to retry the operation if a non-200 status code is received.
        tries: Optional [ :py:class:`int` ]
            The amount of times to retry the operation if a non-200 status code is received. Defaults to 3.
        raw: Optional [ :py:class:`bool` ]
            Whether or not to return the raw result of the operation.

        Returns
        -------
        Optional [ :py:class:`Union` [ :py:class:`List` [ :py:class:`Track` ] , :py:class:`dict` ] ]:
            The raw result or list of tracks that was returned.

        Raises
        ------
        :py:class:`HTTPError`:
            There was a non-200 status code while decoding tracks.
        """

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

            return [Track(track_id=track.get('track'), track_info=track.get('info'), ctx=ctx) for track in data]

        __log__.error(f'DECODETRACKS | Non-200 status code while decoding tracks. All {tries} retries used. | Status code: {response.status}')
        raise HTTPError(f'Non-200 status code while decoding tracks. All {tries} retries used.', status_code=response.status)
