"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Generic, Optional, TYPE_CHECKING, TypeVar, Union

from aiohttp import WSMsgType, WSServerHandshakeError
from discord import Client, VoiceRegion
from discord.ext.commands import AutoShardedBot, Bot, Context
from spotify import HTTPException, NotFound, Playlist

from .exceptions import ObsidianSearchError
from .objects.enums import Op
from .objects.playlist import ObsidianPlaylist
from .objects.stats import ObsidianStats
from .objects.track import ObsidianTrack
from .. import __version__
from ..exceptions import NodeConnectionError, NoMatchesFound
from ..node import BaseNode
from ..objects.enums import LoadType, SearchType, Source
from ..objects.search import SearchResult
from ..pool import NodePool
from ..utils.backoff import ExponentialBackoff


if TYPE_CHECKING:
    from .player import ObsidianPlayer


__all__ = ['ObsidianNode']
__log__: logging.Logger = logging.getLogger('slate.obsidian.node')


BotT = TypeVar('BotT', bound=Union[Client, Bot, AutoShardedBot])
ContextT = TypeVar('ContextT', bound=Context)


SPOTIFY_URL_REGEX = re.compile(r'http(s)?://open.spotify.com/(?P<type>album|playlist|track|artist)/(?P<id>[a-zA-Z0-9]+)')


class ObsidianNode(BaseNode[Any], Generic[BotT, ContextT]):

    def __init__(self, bot: BotT, host: str, port: str, password: str, identifier: str, region: Optional[VoiceRegion] = None, **kwargs) -> None:
        super().__init__(bot, host, port, password, identifier, region, **kwargs)

        self._players: dict[int, ObsidianPlayer[Any, Any]] = {}

        self._headers: dict[str, Any] = {
            'Authorization': self._password,
            'User-Id':       str(self._bot.user.id),
            'Client-Name':   f'Slate/{__version__}',
        }

    def __repr__(self) -> str:
        return f'<slate.ObsidianNode>'

    #

    @property
    def players(self) -> dict[int, ObsidianPlayer[Any, Any]]:
        return self._players

    #

    @property
    def http_url(self) -> str:
        return f'http://{self._host}:{self._port}/'

    @property
    def ws_url(self) -> str:
        return f'ws://{self._host}:{self._port}/magma'

    @property
    def headers(self) -> dict[str, Any]:
        return self._headers

    #

    async def connect(self, *, raise_on_failure: bool = False) -> None:

        try:
            websocket = await self._session.ws_connect(self.ws_url, headers=self._headers)

        except Exception as error:  # TODO: Spicy up this error

            message = f'\'{self._identifier}\' node failed to connect.'

            if isinstance(error, WSServerHandshakeError) and error.status == 4001:
                message = f'\'{self._identifier}\' node failed to connect due to invalid authorization.'

            __log__.error(f'NODE | {message}')
            if raise_on_failure:
                raise NodeConnectionError(message)

        else:

            self._websocket = websocket

            if not self._task:
                self._task = asyncio.create_task(self._listen())

            self._bot.dispatch('slate_node_ready', self)
            __log__.info(f'NODE | \'{self._identifier}\' node connected successfully.')

    async def disconnect(self, *, force: bool = False) -> None:

        for player in self._players.copy().values():
            await player.disconnect(force=force)

        if self.is_connected():
            await self._websocket.close()

        self._websocket = None

        if self._task and not self._task.done:
            self._task.cancel()

        self._task = None

        __log__.info(f'NODE | \'{self._identifier}\' node has been disconnected.')

    async def destroy(self, *, force: bool = False) -> None:

        await self.disconnect(force=force)
        del NodePool._nodes[self._identifier]

        __log__.info(f'NODE | \'{self._identifier}\' node has been destroyed.')

    #

    async def _listen(self) -> None:

        backoff = ExponentialBackoff(base=7)

        while True:

            payload = await self._websocket.receive()

            if payload.type is WSMsgType.CLOSED:

                retry = backoff.delay()
                __log__.warning(f'NODE | \'{self._identifier}\' nodes websocket is closed, attempting reconnection in {round(retry)} seconds.')

                await asyncio.sleep(retry)

                if not self.is_connected():
                    asyncio.create_task(self.connect())

            else:

                data = payload.json()

                try:
                    op = Op(data['op'])
                except ValueError:
                    __log__.warning(f'NODE | \'{self._identifier}\' node received payload with invalid op code. | Payload: {data}')
                    continue
                else:
                    __log__.debug(f'NODE | \'{self._identifier}\' node received payload with op \'{op!r}\'. | Payload: {data}')
                    asyncio.create_task(self._handle_payload(op, data['d']))

    async def _handle_payload(self, op: Op, data: dict[str, Any]) -> None:

        if op is Op.STATS:
            self._stats = ObsidianStats(data)
            return

        if not (player := self._players.get(int(data['guild_id']))):
            return

        if op is Op.PLAYER_EVENT:
            player._dispatch_event(data)
        elif op is Op.PLAYER_UPDATE:
            player._update_state(data)

    #

    async def search(self, search: str, *, ctx: Optional[ContextT] = None, source: Optional[Source] = None) -> Optional[SearchResult[Any, Any]]:

        if (match := SPOTIFY_URL_REGEX.match(search)) and self.spotify is not None:

            search_type = SearchType(match.group('type'))
            spotify_id = match.group('id')

            try:
                if search_type is SearchType.ALBUM:
                    result = await self.spotify.get_album(spotify_id)
                    search_tracks = await result.get_all_tracks()

                elif search_type is SearchType.PLAYLIST:
                    result = Playlist(self.spotify, await self.spotify_http.get_playlist(spotify_id))
                    search_tracks = await result.get_all_tracks()

                elif search_type is SearchType.ARTIST:
                    result = await self.spotify.get_artist(spotify_id)
                    search_tracks = await result.top_tracks()

                else:
                    result = await self.spotify.get_track(spotify_id)
                    search_tracks = [result]

                if not search_tracks:
                    raise NoMatchesFound(search=search, search_type=search_type, source=Source.SPOTIFY)

            except NotFound:
                raise NoMatchesFound(search=search, search_type=search_type, source=Source.SPOTIFY)

            except HTTPException:
                raise ObsidianSearchError({'message': 'Error while accessing spotify API.', 'severity': 'COMMON'})

            tracks = [
                ObsidianTrack(
                        ctx=ctx, id='',
                        info={
                            'title':       track.name or 'UNKNOWN',
                            'author':      ', '.join(artist.name for artist in track.artists) if track.artists else 'UNKNOWN',
                            'uri':         track.url or search,
                            'identifier':  track.id or 'UNKNOWN',
                            'length':      track.duration or 0,
                            'position':    0,
                            'is_stream':   False,
                            'is_seekable': False,
                            'source_name': 'spotify',
                            'thumbnail':   track.images[0].url if track.images else None
                        }
                ) for track in search_tracks
            ]

            return SearchResult(source=Source.SPOTIFY, type=search_type, result=result, tracks=tracks)

        else:

            if source is Source.YOUTUBE:
                search = f'ytsearch:{search}'
            elif source is Source.SOUNDCLOUD:
                search = f'scsearch:{search}'
            elif source is Source.YOUTUBE_MUSIC:
                search = f'ytmsearch:{search}'

            data = await self._request(method='GET', endpoint='/loadtracks', identifier=search)

            load_type = LoadType(data['load_type'])
            message = f'SEARCH | \'{load_type!r}\' for search: {search} | Data: {data}'

            if load_type is LoadType.LOAD_FAILED:
                __log__.warning(message)
                raise ObsidianSearchError(data['exception'])

            if load_type is LoadType.NO_MATCHES or not data['tracks']:
                __log__.info(message)
                raise NoMatchesFound(search=search, search_type=SearchType.TRACK, source=source)

            if load_type is LoadType.PLAYLIST_LOADED:

                __log__.info(message)

                info = data['playlist_info']
                info['uri'] = search  # If a playlist is found, it should only ever be by direct link, so this should be fine.

                playlist = ObsidianPlaylist(info=info, tracks=data['tracks'], ctx=ctx)
                return SearchResult(source=playlist.source, type=SearchType.PLAYLIST, result=playlist, tracks=playlist.tracks)

            if load_type in [LoadType.TRACK_LOADED, LoadType.SEARCH_RESULT]:

                __log__.info(message)

                tracks = [ObsidianTrack(id=track['track'], info=track['info'], ctx=ctx) for track in data['tracks']]
                return SearchResult(source=tracks[0].source, type=SearchType.TRACK, result=tracks, tracks=tracks)

    #

    async def decode_track(
            self, track_id: str, *, ctx: Optional[ContextT] = None, retry: bool = True, tries: int = 3, raw: bool = False
    ) -> Optional[Union[ObsidianTrack[Any], dict[str, Any]]]:

        backoff = ExponentialBackoff()

        for _ in range(tries):

            async with self.session.get(url=f'{self.http_url}/decodetrack', headers={'Authorization': self._password}, params={'track': track_id}) as response:

                if response.status != 200:

                    if retry:
                        time = backoff.delay()
                        __log__.warning(f'DECODETRACK | Non-200 status code while decoding track. Retrying in {round(time)}s. | Status code: {response.status}')
                        await asyncio.sleep(time)
                        continue

                    __log__.error(f'DECODETRACK | Non-200 status code while decoding track. Not retrying. | Status code: {response.status}')
                    raise ValueError('Non-200 status code while decoding track.')

                data = await response.json()

            if raw:
                return data

            return ObsidianTrack(id=track_id, info=data.get('info', None) or data, ctx=ctx)

        __log__.error(f'DECODETRACK | Non-200 status code while decoding track. All {tries} retries used. | Status code: {response.status}')
        raise ValueError(f'Non-200 status code while decoding track. All {tries} retries used.')

    async def decode_tracks(
            self, track_ids: list[str], *, ctx: Optional[ContextT] = None, retry: bool = True, tries: int = 3,  raw: bool = False
    ) -> Optional[Union[list[ObsidianTrack[Any]], dict[str, Any]]]:

        backoff = ExponentialBackoff()

        for _ in range(tries):

            async with self.session.post(url=f'{self.http_url}/decodetracks', headers={'Authorization': self._password}, data=json.dumps(track_ids)) as response:

                if response.status != 200:

                    if retry:
                        time = backoff.delay()
                        __log__.warning(f'DECODETRACKS | Non-200 status code while decoding tracks. Retrying in {round(time)}s. | Status code: {response.status}')
                        await asyncio.sleep(time)
                        continue

                    __log__.error(f'DECODETRACKS | Non-200 status code while decoding tracks. Not retrying. | Status code: {response.status}')
                    raise ValueError('Non-200 status code while decoding tracks.')

                data = await response.json()

            if raw:
                return data

            return [ObsidianTrack(id=track.get('track'), info=track.get('info'), ctx=ctx) for track in data]

        __log__.error(f'DECODETRACKS | Non-200 status code while decoding tracks. All {tries} retries used. | Status code: {response.status}')
        raise ValueError(f'Non-200 status code while decoding tracks. All {tries} retries used.')
