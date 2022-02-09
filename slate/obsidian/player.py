# Future
from __future__ import annotations

# Standard Library
import logging
import time
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

# Packages
import discord
import discord.types.voice
from discord.ext import commands

# My stuff
from slate.obsidian.node import NodePool
from slate.obsidian.objects.enums import Op
from slate.obsidian.objects.events import (
    TrackEnd,
    TrackException,
    TrackStart,
    TrackStuck,
    WebsocketClosed,
    WebsocketOpen,
)
from slate.obsidian.objects.filters import Filter
from slate.obsidian.objects.track import Track
from slate.player import BasePlayer


if TYPE_CHECKING:

    # My stuff
    from slate.obsidian.node import Node


__all__ = (
    "Player",
)
__log__: logging.Logger = logging.getLogger("slate.obsidian.player")


BotT = TypeVar("BotT", bound=Union[discord.Client, discord.AutoShardedClient, commands.Bot, commands.AutoShardedBot])
ContextT = TypeVar("ContextT", bound=commands.Context)
PlayerT = TypeVar("PlayerT", bound="Player")


class Player(BasePlayer, Generic[BotT, ContextT, PlayerT]):

    def __call__(self, client: BotT, channel: discord.VoiceChannel) -> Player[BotT, ContextT, PlayerT]:

        self.client: CD = client
        self.channel: discord.VoiceChannel = channel

        self._node = NodePool.get_node()
        self._node._players[channel.guild.id] = self

        return self

    def __init__(
        self,
        client: BotT = MISSING,
        channel: discord.VoiceChannel = MISSING,
    ) -> None:

        super().__init__(
            client,
            channel
        )

        self.client: BotT = MISSING
        self.channel: discord.VoiceChannel = MISSING
        self._node: Node[BotT, ContextT, PlayerT] = MISSING

        self._voice_server_update_data: discord.types.voice.VoiceServerUpdate | None = None
        self._session_id: str | None = None

        self._last_update: float = 0

        self._frames_lost: int = 0
        self._frames_sent: int = 0
        self._frame_data_usable: bool = True

        self._filter: Filter | None = None
        self._current: Track[ContextT] | None = None

        self._current_track_id: str | None = None
        self._position: float = 0
        self._paused: bool = False

        self._timestamp: int = 0

    def __repr__(self) -> str:
        return "<slate.obsidian.Player>"

    #

    def is_playing(self) -> bool:
        return self.is_connected() is True and self._current is not None

    def is_paused(self) -> bool:
        return self._paused is True

    # Properties

    @property
    def filter(self) -> Filter | None:
        return self._filter

    @property
    def current(self) -> Track[ContextT] | None:
        return self._current

    @property
    def current_track_id(self) -> str | None:
        return self._current_track_id

    @property
    def position(self) -> float:

        if not self.is_playing():
            return 0

        assert self._current is not None

        if self._paused:
            return min(self._position, self._current.length)

        position = self._position + ((time.time() * 1000) - self._last_update)

        if position > self._current.length:
            return 0

        return position

    @property
    def paused(self) -> bool:
        return self._paused

    # Implemented abstract methods (from discord.py)

    async def on_voice_server_update(self, data: discord.types.voice.VoiceServerUpdate) -> None:

        __log__.debug(f"Player '{self.channel.guild.id}' received VOICE_SERVER_UPDATE.\nData: {data}")

        self._voice_server_update_data = data
        await self._dispatch_voice_update()

    async def on_voice_state_update(self, data: discord.types.voice.GuildVoiceState) -> None:

        __log__.debug(f"Player '{self.channel.guild.id}' received VOICE_STATE_UPDATE.\nData: {data}")

        self._session_id = data.get("session_id")
        await self._dispatch_voice_update()

    # Implemented abstract methods

    async def _dispatch_voice_update(self) -> None:

        if not self._session_id or not self._voice_server_update_data:
            return

        await self._node._send_payload(Op.SUBMIT_VOICE_UPDATE, data={"session_id": self._session_id, **self._voice_server_update_data})

    def _dispatch_event(self, data: dict[str, Any]) -> None:

        event_type = data["type"]

        if event_type == "WEBSOCKET_OPEN":
            event = WebsocketOpen(data)
        elif event_type == "WEBSOCKET_CLOSED":
            event = WebsocketClosed(data)
        elif event_type == "TRACK_START":
            event = TrackStart(data)
        elif event_type == "TRACK_END":
            event = TrackEnd(data)
        elif event_type == "TRACK_STUCK":
            event = TrackStuck(data)
        elif event_type == "TRACK_EXCEPTION":
            event = TrackException(data)
        else:
            __log__.error(f"Player '{self.channel.guild.id}' received unknown event type.\nData: {data} ")
            return

        __log__.info(f"Player '{self.channel.guild.id}' dispatched event with type {event.type!r}.\nData: {data}")
        self.client.dispatch(f"obsidian_{event.type.value.lower()}", self, event)

    def _update_state(self, data: dict[str, Any]) -> None:

        self._last_update = time.time() * 1000

        frames = data.get("frames", {})
        self._frames_lost = frames.get("lost", 0)
        self._frames_sent = frames.get("sent", 0)
        self._frame_data_usable = frames.get("usable", False)

        current_track = data.get("current_track", {})
        self._current_track_id = current_track.get("track")
        self._position = current_track.get("position", 0)
        self._paused = current_track.get("paused", False)

        self._timestamp = data.get("timestamp", 0)

    #

    async def connect(
        self,
        *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_deaf: bool = False
    ) -> None:

        await self.channel.guild.change_voice_state(channel=self.channel, self_deaf=self_deaf)
        __log__.info(f"Player '{self.channel.guild.id}' connected to voice channel '{self.channel.id}'.")

    async def disconnect(
        self,
        *,
        force: bool = False
    ) -> None:

        if self.is_connected() is False and not force:
            return

        await self.channel.guild.change_voice_state(channel=None)

        if self._node.is_connected() is True:
            await self.stop(force=force)
            await self._node._send_payload(Op.PLAYER_DESTROY, data={"guild_id": str(self.channel.guild.id)})

        del self._node._players[self.channel.guild.id]
        self.cleanup()

        __log__.info(f"Player '{self.channel.guild.id}' was disconnected.")

    async def move_to(
        self,
        channel: discord.VoiceChannel,
        /,
    ) -> None:

        await self.channel.guild.change_voice_state(channel=channel)
        __log__.info(f"Player '{self.channel.guild.id}' moved to voice channel '{channel.id}'.")

        self.channel = channel

    #

    async def play(
        self,
        track: Track[ContextT],
        /,
        *,
        start_time: int = 0,
        end_time: int = 0,
        no_replace: bool = False
    ) -> None:

        payload: dict[str, Any] = {
            "guild_id": str(self.channel.guild.id),
            "track":    str(track.id),
        }
        if 0 < start_time < track.length:
            payload["start_time"] = start_time
        if 0 < end_time < track.length:
            payload["end_time"] = end_time
        if no_replace:
            payload["no_replace"] = no_replace

        await self._node._send_payload(Op.PLAY_TRACK, data=payload)
        __log__.info(f"Player '{self.channel.guild.id}' is playing the track {track!r}.")

        self._position = 0
        self._last_update = 0
        self._current = track

    async def stop(
        self,
        *,
        force: bool = False
    ) -> None:

        if self._current is None and not force:
            return

        await self._node._send_payload(Op.STOP_TRACK, data={"guild_id": str(self.channel.guild.id)})
        __log__.info(f"Player '{self.channel.guild.id}' stopped the current track.")

        self._current = None

    async def set_pause(
        self,
        pause: bool,
        /,
    ) -> None:

        await self._node._send_payload(Op.PLAYER_PAUSE, data={"guild_id": str(self.channel.guild.id), "state": pause})
        __log__.info(f"Player '{self.channel.guild.id}' set its paused state to {pause!r}.")

        self._paused = pause

    async def set_filter(
        self,
        filter: Filter,
        /,
        *,
        seek: bool = True
    ) -> None:

        await self._node._send_payload(Op.PLAYER_FILTERS, data={"guild_id": str(self.channel.guild.id), "filters": {**filter._payload}})
        __log__.info(f"Player '{self.channel.guild.id}' applied filter {filter!r}")

        self._filter = filter

        if seek:
            await self.set_position(self.position)

    async def set_position(
        self,
        position: float,
        /,
        *,
        force: bool = False
    ) -> None:

        if (self._current is None or 0 > position > self._current.length) and not force:
            return

        await self._node._send_payload(Op.PLAYER_SEEK, data={"guild_id": str(self.channel.guild.id), "position": round(position)})
        __log__.info(f"Player '{self.channel.guild.id}' set its position to '{self.position}'.")

        self._position = position
        self._last_update = time.time() * 1000

    #

    async def pause(self) -> None:
        return await self.set_pause(True)

    async def resume(self) -> None:
        return await self.set_pause(False)

    async def seek(
        self,
        position: float,
        /,
        *,
        force: bool = False
    ) -> None:
        return await self.set_position(position, force=force)
