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

import logging
import time
from typing import Any, Generic, Optional, TypeVar, Union

from discord import Client, VoiceChannel
from discord.ext.commands import AutoShardedBot, Bot

from .node import ObsidianNode
from .objects import events
from .objects.enums import Op
from .objects.filters import Filter
from .objects.track import ObsidianTrack
from ..player import BasePlayer
from ..pool import NodePool


__all__ = ['ObsidianPlayer']
__log__: logging.Logger = logging.getLogger('slate.obsidian.player')


BotT = TypeVar('BotT', bound=Union[Client, Bot, AutoShardedBot])
TrackT = TypeVar('TrackT', bound=ObsidianTrack[Any])


class ObsidianPlayer(BasePlayer[Any], Generic[BotT, TrackT]):

    def __init__(self, client: BotT, channel: VoiceChannel) -> None:
        super().__init__(client, channel)

        self._node: ObsidianNode[Any, Any] = NodePool.get_node(node_cls=ObsidianNode)
        self._node.players[self.guild.id] = self

        self._voice_server_update_data: Optional[dict[str, Any]] = None
        self._session_id: Optional[str] = None

        self._last_update: float = 0

        self._frames_sent: Optional[int] = None
        self._frames_lost: Optional[int] = None
        self._frame_data_usable: bool = True

        self._current_track_id: Optional[str] = None
        self._position: float = 0
        self._paused: bool = False

        self._filter: Optional[Filter] = None
        self._current: Optional[TrackT] = None

    def __repr__(self) -> str:
        return f'<slate.ObsidianPlayer>'

    #

    @property
    def node(self) -> ObsidianNode[Any, Any]:
        return self._node

    #

    async def on_voice_server_update(self, data: dict[str, Any]) -> None:

        __log__.debug(f'PLAYER | \'{self._guild.id}\' received VOICE_SERVER_UPDATE | Data: {data}')

        self._voice_server_update_data = data
        await self._dispatch_voice_update()

    async def on_voice_state_update(self, data: dict[str, Any]) -> None:

        __log__.debug(f'PLAYER | \'{self._guild.id}\' received VOICE_STATE_UPDATE | Data: {data}')

        if not (channel_id := data.get('channel_id')):
            self.channel = None
            self._session_id = None
            self._voice_server_update_data = None
            return

        self.channel = self.guild.get_channel(int(channel_id))
        self._session_id = data.get('session_id')
        await self._dispatch_voice_update()

    #

    async def _dispatch_voice_update(self) -> None:

        if not self._session_id or not self._voice_server_update_data:
            return

        await self._node.send(op=Op.SUBMIT_VOICE_UPDATE, **{'session_id': self._session_id, **self._voice_server_update_data})

    def _dispatch_event(self, data: dict[str, Any]) -> None:

        if not (event := getattr(events, f'Obsidian{"".join([word.title() for word in data.get("type").split("_")])}', None)):
            __log__.error(f'PLAYER | \'{self._guild.id}\' received unknown event type. | Data: {data} ')
            return

        event = event(data)

        __log__.info(f'PLAYER | \'{self._guild.id}\' dispatching {event.type!r} event. | Data: {data}')
        self._bot.dispatch(f'obsidian_{event.type.value.lower()}', self, event)

    def _update_state(self, data: dict[str, Any]) -> None:

        __log__.debug(f'PLAYER | \'{self.guild.id}\' updating state. | State: {data}')

        self._last_update = time.time() * 1000

        frames = data.get('frames', {})
        self._frames_sent = frames.get('sent')
        self._frames_lost = frames.get('lost')
        self._frame_data_usable = frames.get('usable', False)

        current_track = data.get('current_track', {})
        self._current_track_id = current_track.get('track')
        self._position = current_track.get('position', 0)
        self._paused = current_track.get('paused', False)

    #

    async def connect(self, *, timeout: Optional[float] = None, reconnect: Optional[bool] = None, self_deaf: bool = False) -> None:

        await self._guild.change_voice_state(channel=self.channel, self_deaf=self_deaf)
        __log__.info(f'PLAYER | \'{self._guild.id}\' connected to voice channel \'{self.channel.id}\'.')

    async def disconnect(self, *, force: bool = False) -> None:

        if not self.is_connected() and not force:
            return

        await self._guild.change_voice_state(channel=None)

        if self._node.is_connected():
            await self.stop(force=force)
            await self._node.send(op=Op.PLAYER_DESTROY, **{'guild_id': str(self._guild.id)})

        del self._node._players[self._guild.id]
        self.cleanup()

        __log__.info(f'PLAYER | \'{self.guild.id}\' was disconnected.')

    async def move_to(self, channel: VoiceChannel) -> None:

        await self.set_pause(True)

        await self._guild.change_voice_state(channel=channel)
        __log__.info(f'PLAYER | \'{self._guild.id}\' moved to voice channel \'{channel.id}\'.')

        self.channel = channel

        await self.set_pause(False)

    #

    @property
    def current_track_id(self) -> Optional[str]:
        return self._current_track_id

    @property
    def position(self) -> float:

        if not self.is_playing():
            return 0

        if self._paused:
            return min(self._position, self._current.length)

        position = self._position + ((time.time() * 1000) - self._last_update)

        if position > self._current.length:
            return 0

        return position

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def filter(self) -> Optional[Filter]:
        return self._filter

    @property
    def current(self) -> Optional[TrackT]:
        return self._current

    #

    def is_playing(self) -> bool:
        return self.is_connected() and self._current is not None

    def is_paused(self) -> bool:
        return self._paused

    #

    async def play(self, track: TrackT, *, start_time: int = 0, end_time: int = 0, no_replace: bool = False) -> None:

        self._position = 0
        self._last_update = 0

        payload: dict[str, Any] = {
            'guild_id': str(self._guild.id),
            'track':    str(track.id),
        }
        if 0 < start_time < track.length:
            payload['start_time'] = start_time
        if 0 < end_time < track.length:
            payload['end_time'] = end_time
        if no_replace:
            payload['no_replace'] = no_replace

        await self._node.send(op=Op.PLAY_TRACK, **payload)
        __log__.info(f'Player \'{self._guild.id}\' is playing the track {track!r}.')

        self._current = track

    async def stop(self, *, force: bool = False) -> None:

        if not self._current and not force:
            return

        await self._node.send(op=Op.STOP_TRACK, **{'guild_id': str(self._guild.id)})
        __log__.info(f'Player \'{self._guild.id}\' stopped the current track.')

        self._current = None

    async def set_pause(self, pause: bool) -> None:

        await self._node.send(op=Op.PLAYER_PAUSE, **{'guild_id': str(self._guild.id), 'state': pause})
        __log__.info(f'Player \'{self._guild.id}\' set its paused state to \'{pause}\'.')

        self._paused = pause

    async def set_filter(self, filter: Filter, *, seek: bool = False) -> None:

        await self._node.send(op=Op.PLAYER_FILTERS, **{'guild_id': str(self._guild.id), 'filters': {**filter._payload}})
        __log__.info(f'Player \'{self._guild.id}\' applied filter {filter!r}')

        if seek:
            await self.set_position(self.position)

        self._filter = filter

    async def set_position(self, position: float) -> None:

        if not self._current or 0 > position > self._current.length:
            return

        await self._node.send(op=Op.PLAYER_SEEK, **{'guild_id': str(self._guild.id), 'position': round(position)})
        __log__.info(f'Player \'{self.guild.id}\' set its position to \'{self.position}\'.')

        self._position = position
        self._last_update = time.time() * 1000

    #

    async def pause(self) -> None:
        return await self.set_pause(True)

    async def resume(self) -> None:
        return await self.set_pause(False)

    async def seek(self, position: float) -> None:
        return await self.set_position(position)
