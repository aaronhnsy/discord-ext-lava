from __future__ import annotations

import logging
import time
from typing import Any, Generic, List, Optional, TYPE_CHECKING, TypeVar, Union

import discord
from discord import VoiceProtocol
from discord.ext import commands


if TYPE_CHECKING:
    from .node import ObsidianNode

BotType = TypeVar('BotType', bound=Union[discord.Client, commands.Bot, commands.AutoShardedBot])
TrackType = TypeVar('TrackType', bound=ObsidianTrack)

__all__ = ['LavalinkPlayer']
__log__: logging.Logger = logging.getLogger('slate.obsidian.player')


class LavalinkPlayer(VoiceProtocol, Generic[BotType, TrackType]):

    def __init__(self, client: BotType, channel: discord.VoiceChannel) -> None:
        super().__init__(client=client, channel=channel)

        self.client: BotType = client
        self.channel: discord.VoiceChannel = channel

        self._bot: BotType = self.client
        self._guild: discord.Guild = channel.guild

        self._node: Optional[ObsidianTrack] = None

        self._voice_server_update_data: Optional[dict] = None
        self._session_id: Optional[str] = None

        self._last_update: int = 0

        self._frames_sent: int = 0
        self._frames_lost: int = 0
        self._frame_data_usable: bool = True

        self._current_track_id: Optional[str] = None
        self._position: int = 0
        self._paused: bool = False

        self._filter: Optional[ObsidianFilter] = None

        self._current: Optional[ObsidianTrack] = None

    def __repr__(self) -> str:
        return f'<slate.ObsidianPlayer channel=\'{getattr(self.channel, "id", None)}\' is_connected={self.is_connected} is_playing={self.is_playing} paused={self.paused}>'

    #

    @property
    def bot(self) -> BotType:
        return self._bot

    @property
    def guild(self) -> discord.Guild:
        return self._guild

    @property
    def node(self) -> Optional[ObsidianNode]:
        return self._node

    #

    @property
    def current_track_id(self) -> Optional[str]:
        return self._current_track_id

    @property
    def position(self) -> float:

        if not self.current:
            return 0

        if self._paused:
            return min(self._position, self.current.length)

        position = self._position + ((time.time() * 1000) - self._last_update)

        if position > self.current.length:
            return 0

        return position

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def filter(self) -> Optional[ObsidianFilter]:
        return self._filter

    #

    @property
    def current(self) -> Optional[ObsidianTrack]:
        return self._current

    #

    @property
    def is_connected(self) -> bool:
        return self.channel is not None

    @property
    def is_playing(self) -> bool:
        return self.is_connected and self._current is not None

    #

    @property
    def listeners(self) -> List[discord.Member]:
        return [member for member in getattr(self.channel, 'members', []) if not member.bot and not member.voice.deaf or not member.voice.self_deaf]

    #

    async def on_voice_server_update(self, data: dict[str, Any]) -> None:

        __log__.debug(f'PLAYER | Received VOICE_SERVER_UPDATE | Data: {data}')

        self._voice_server_update_data = data
        await self._dispatch_voice_update()

    async def on_voice_state_update(self, data: dict[str, Any]) -> None:

        __log__.debug(f'PLAYER | Received VOICE_STATE_UPDATE | Data: {data}')

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

        await self.node._send(op=Op.SUBMIT_VOICE_UPDATE, **{'session_id': self._session_id, **self._voice_server_update_data})

    def _dispatch_event(self, data: dict) -> None:

        if not (event := getattr(events, f'Obsidian{"".join([word.title() for word in data.get("type").split("_")])}', None)):
            __log__.error(f'PLAYER | Unknown event type received. | Data: {data} ')
            return

        data['player'] = self
        event = event(data)

        __log__.info(f'PLAYER | Dispatching {event.type.value} event. | Data: {data}')
        self.bot.dispatch(f'obsidian_{event.type.value.lower()}', event)

    async def _update_state(self, data: dict) -> None:

        __log__.info(f'PLAYER | Updating player state. | State: {data}')

        self._last_update = time.time() * 1000

        frames = data.get('frames', {})
        self._frames_sent = frames.get('sent')
        self._frames_lost = frames.get('lost')
        self._frame_data_usable = frames.get('usable')

        current_track = data.get('current_track', {})
        self._current_track_id = current_track.get('track')
        self._last_position = current_track.get('position')
        self._paused = current_track.get('paused')

    #

    async def connect(self, *, timeout: float = None, reconnect: bool = None) -> None:

        await self.guild.change_voice_state(channel=self.channel)
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' connected to voice channel \'{self.channel.id}\'.')

    async def disconnect(self, *, force: bool = False) -> None:

        if not self.is_connected and not force:
            return

        await self.guild.change_voice_state(channel=None)
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' disconnected from voice channel \'{self.channel.id}\'.')

        if self.node.is_connected:
            await self.stop(force=force)
            await self.node._send(op=Op.PLAYER_DESTROY, **{'guild_id': str(self.guild.id)})

        del self.node.players[self.guild.id]
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' was destroyed.')

        self.cleanup()

    async def move_to(self, channel: discord.VoiceChannel) -> None:

        await self.set_pause(True)

        await self.guild.change_voice_state(channel=channel)
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' moved to voice channel \'{channel.id}\'.')

        self.channel = channel

        await self.set_pause(False)

    #

    async def play(self, track: TrackType[Any], *, start_time: int = 0, end_time: int = 0, no_replace: bool = False) -> None:

        self._position = 0
        self._last_update = 0

        payload = {
            'guild_id': str(self.guild.id),
            'track':    str(track.id),
        }
        if 0 < start_time < track.length:
            payload['start_time'] = start_time
        if 0 < end_time < track.length:
            payload['end_time'] = end_time
        if no_replace:
            payload['no_replace'] = no_replace

        await self.node._send(op=Op.PLAY_TRACK, **payload)
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' is playing the track {track!r}.')

        self._current = track

    async def stop(self, *, force: bool = False) -> None:

        if not self.current and not force:
            return

        await self.node._send(op=Op.STOP_TRACK, **{'guild_id': str(self.guild.id)})
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' stopped the current track.')

        self._current = None

    async def set_pause(self, state: bool) -> None:

        await self.node._send(op=Op.PLAYER_PAUSE, **{'guild_id': str(self.guild.id), 'state': state})
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' has set its paused state to \'{state}\'.')

        self._paused = state

    async def set_filter(self, filter: ObsidianFilter, *, seek: bool = False) -> None:

        await self.node._send(op=Op.PLAYER_FILTERS, **{'guild_id': str(self.guild.id), 'filters': {**filter._payload}})
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' has applied filter {filter!r}')

        if seek:
            await self.set_position(self.position)

        self._filter = filter

    async def set_position(self, position: float) -> None:

        if not self.current or 0 > position > self.current.length:
            return

        await self.node._send(op=Op.PLAYER_SEEK, **{'guild_id': str(self.guild.id), 'position': round(position)})
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' has set its position to \'{self.position}\'.')

        self._position = position
        self._last_update = time.time() * 1000
