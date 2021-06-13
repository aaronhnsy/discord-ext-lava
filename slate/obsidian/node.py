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
from typing import Any, Generic, Optional, TYPE_CHECKING, TypeVar, Union

import aiohttp
import discord
from discord.ext import commands

from .objects.enums import Op
from .objects.stats import ObsidianStats
from .. import __version__
from ..exceptions import NodeConnectionError
from .exceptions import HTTPError, TrackLoadError
from ..node import BaseNode
from ..pool import NodePool
from ..utils.backoff import ExponentialBackoff
from .objects.track import ObsidianTrack
from .objects.playlist import ObsidianPlaylist

if TYPE_CHECKING:
    from .player import ObsidianPlayer


__all__ = ['ObsidianNode']
__log__ = logging.getLogger('slate.obsidian.node')


BotT = TypeVar('BotT', bound=Union[discord.Client, commands.Bot, commands.AutoShardedBot])
ContextT = TypeVar('ContextT', bound=commands.Context)


class ObsidianNode(BaseNode[Any], Generic[BotT, ContextT]):

    def __init__(self, bot: BotT, host: str, port: str, password: str, identifier: str, region: Optional[discord.VoiceRegion], **kwargs) -> None:
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

            if isinstance(error, aiohttp.WSServerHandshakeError) and error.status == 4001:
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

            if payload.type is aiohttp.WSMsgType.CLOSED:

                retry = backoff.delay()
                __log__.warning(f'NODE | \'{self._identifier}\' nodes websocket is closed, attempting reconnection in {round(retry)} seconds.')

                await asyncio.sleep(retry)

                if not self.is_connected():
                    asyncio.create_task(self.connect())

            else:

                data = payload.json()

                try:
                    op = Op(data.get('op', None))
                except ValueError:
                    __log__.warning(f'NODE | \'{self._identifier}\' node received payload with invalid op code. | Payload: {data}')
                    continue

                else:
                    __log__.debug(f'NODE | \'{self._identifier}\' node received payload with op {op!r}. | Payload: {data}')
                    asyncio.create_task(self._handle_payload(op, data['d']))

    async def _handle_payload(self, op, data: dict[str, Any]) -> None:

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

    async def search(
            self, query: str, *, ctx: Optional[ContextT] = None, retry: bool = True, tries: int = 3, raw: bool = False
    ) -> Optional[Union[ObsidianPlaylist[Any], list[ObsidianTrack[Any]], dict[str, Any]]]:

        backoff = ExponentialBackoff()

        for _ in range(tries):

            async with self._session.get(url=f'{self.http_url}/loadtracks', headers={'Authorization': self._password}, params={'identifier': query}) as response:

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
                return ObsidianPlaylist(info=playlist_info, tracks=data.get('tracks'), ctx=ctx)

            if load_type in ['SEARCH_RESULT', 'TRACK_LOADED']:
                __log__.info(f'LOADTRACKS | SEARCH_RESULT/TRACK_LOADED for query: {query} | Data: {data}')
                return [ObsidianTrack(id=track.get('track'), info=track.get('info'), ctx=ctx) for track in data.get('tracks')]

        __log__.error(f'LOADTRACKS | Non-200 status code while loading tracks. All {tries} retries used. | Status code: {response.status}')
        raise HTTPError(f'Non-200 status code while loading tracks. All {tries} retries used.', status_code=response.status)

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
                    raise HTTPError('Non-200 status code while decoding track.', status_code=response.status)

                data = await response.json()

            if raw:
                return data

            return ObsidianTrack(id=track_id, info=data.get('info', None) or data, ctx=ctx)

        __log__.error(f'DECODETRACK | Non-200 status code while decoding track. All {tries} retries used. | Status code: {response.status}')
        raise HTTPError(f'Non-200 status code while decoding track. All {tries} retries used.', status_code=response.status)

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
                    raise HTTPError('Non-200 status code while decoding tracks.', status_code=response.status)

                data = await response.json()

            if raw:
                return data

            return [ObsidianTrack(id=track.get('track'), info=track.get('info'), ctx=ctx) for track in data]

        __log__.error(f'DECODETRACKS | Non-200 status code while decoding tracks. All {tries} retries used. | Status code: {response.status}')
        raise HTTPError(f'Non-200 status code while decoding tracks. All {tries} retries used.', status_code=response.status)
