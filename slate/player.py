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
from .objects.enums import NodeType
from .objects.events import TrackEnd, TrackException, TrackStart, TrackStuck, WebsocketClosed, WebsocketOpen
from .objects.filters import Filter
from .objects.track import Track
from .pool import Pool
from .utils import MISSING


if TYPE_CHECKING:
    # My stuff
    from .node import Node


__all__ = (
    "Player",
)
__log__: logging.Logger = logging.getLogger("slate.player")


OBSIDIAN_EVENT_MAPPING: dict[str, Any] = {
    "WEBSOCKET_OPEN": WebsocketOpen,
    "WEBSOCKET_CLOSED": WebsocketClosed,
    "TRACK_START": TrackStart,
    "TRACK_END": TrackEnd,
    "TRACK_STUCK": TrackStuck,
    "TRACK_EXCEPTION": TrackException,
}

LAVALINK_EVENT_MAPPING = {
    "WebsocketClosedEvent": WebsocketClosed,
    "TrackStartEvent": TrackStart,
    "TrackEndEvent": TrackEnd,
    "TrackStuckEvent": TrackStuck,
    "TrackExceptionEvent": TrackException,
}

BotT = TypeVar("BotT", bound=Union[discord.Client, discord.AutoShardedClient, commands.Bot, commands.AutoShardedBot])
ContextT = TypeVar("ContextT", bound=commands.Context)
PlayerT = TypeVar("PlayerT", bound="Player")
VoiceChannel = discord.VoiceChannel | discord.StageChannel


class Player(discord.VoiceProtocol, Generic[BotT, ContextT, PlayerT]):

    def __call__(self, client: BotT, channel: VoiceChannel) -> Player[BotT, ContextT, PlayerT]:

        self.client: BotT = client
        self.channel: VoiceChannel = channel

        self._node: Node[BotT, ContextT, PlayerT] = Pool.get_node()  # type: ignore
        self._node._players[channel.guild.id] = self  # type: ignore

        return self

    def __init__(self) -> None:

        super().__init__(
            client=MISSING,
            channel=MISSING
        )

        self.client: BotT = MISSING
        self.channel: VoiceChannel = MISSING
        self._node: Node[BotT, ContextT, PlayerT] = MISSING

        self._voice_server_update_data: discord.types.voice.VoiceServerUpdate | None = None
        self._session_id: str | None = None

        self._current_track_id: str | None = None
        self._current: Track[ContextT] | None = None
        self._paused: bool = False

        self._last_update: float = 0
        self._position: float = 0
        self._timestamp: float = 0

        self._filter: Filter | None = None

    def __repr__(self) -> str:
        return "<slate.Player>"

    # Properties / Utilities

    @property
    def bot(self) -> BotT:
        return self.client

    @property
    def voice_channel(self) -> VoiceChannel:
        return self.channel

    @property
    def node(self) -> Node[BotT, ContextT, PlayerT]:
        return self._node

    @property
    def current(self) -> Track[ContextT] | None:
        return self._current

    @property
    def paused(self) -> bool:
        return self._paused

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
    def filter(self) -> Filter | None:
        return self._filter

    def is_connected(self) -> bool:
        return self.channel is not None

    def is_playing(self) -> bool:
        return self.is_connected() is True and self._current is not None

    def is_paused(self) -> bool:
        return self._paused is True

    #

    async def on_voice_server_update(self, data: discord.types.voice.VoiceServerUpdate) -> None:

        __log__.debug(f"Player '{self.voice_channel.guild.id}' received VOICE_SERVER_UPDATE.\nData: {data}")

        self._voice_server_update_data = data
        await self._dispatch_voice_update()

    async def on_voice_state_update(self, data: discord.types.voice.GuildVoiceState) -> None:

        __log__.debug(f"Player '{self.voice_channel.guild.id}' received VOICE_STATE_UPDATE.\nData: {data}")

        self._session_id = data.get("session_id")
        await self._dispatch_voice_update()

    async def _dispatch_voice_update(self) -> None:

        if not self._session_id or not self._voice_server_update_data:
            return

        if self._node._type is NodeType.OBSIDIAN:
            op = 0
            data = {
                "session_id": self._session_id,
                **self._voice_server_update_data
            }
        else:
            op = "voiceUpdate"
            data = {
                "guildId": self._voice_server_update_data["guild_id"],
                "sessionId": self._session_id,
                **self._voice_server_update_data
            }

        await self._node._send_payload(op, data=data)

    #

    def _dispatch_event(self, data: dict[str, Any]) -> None:

        _type = data["type"]

        if not (event := OBSIDIAN_EVENT_MAPPING.get(_type) if self._node._type is NodeType.OBSIDIAN else LAVALINK_EVENT_MAPPING.get(_type)):
            __log__.error(f"Player '{self.channel.guild.id}' received an event with an unknown type '{_type}'.\nData: {data}")
            return

        event = event(data)

        __log__.info(f"Player '{self.channel.guild.id}' dispatched an event with type '{_type}'.\nData: {data}")
        self.bot.dispatch(f"slate_{event.type.lower()}", self, event)

    def _update_state(self, data: dict[str, Any]) -> None:

        self._last_update = time.time() * 1000

        if self._node._type is NodeType.OBSIDIAN:

            current: dict[str, Any] = data["current_track"]
            self._current_track_id = current["track"]
            self._paused = current["paused"]
            self._position = current["position"]
            self._timestamp = data["timestamp"]
            # TODO: Parse filters from data["filters"]

        else:
            state: dict[str, Any] = data["state"]
            self._position = state["position"]
            self._timestamp = state["time"]

    #

    async def connect(
        self,
        *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_mute: bool = False,
        self_deaf: bool = True,
    ) -> None:

        await self.channel.guild.change_voice_state(channel=self.voice_channel, self_mute=self_mute, self_deaf=self_deaf)
        __log__.info(f"Player '{self.voice_channel.guild.id}' connected to voice channel '{self.voice_channel.id}'.")

    async def disconnect(
        self,
        *,
        force: bool = False
    ) -> None:

        __log__.info(f"Player '{self.voice_channel.guild.id}' disconnected from voice channel '{self.voice_channel.id}'.")
        await self.channel.guild.change_voice_state(channel=None)

        if self._node.is_connected():

            await self.stop(force=force)

            if self._node._type is NodeType.OBSIDIAN:
                op = 11
                data = {"guild_id": str(self.voice_channel.guild.id)}
            else:
                op = "destroy"
                data = {"guildId": str(self.voice_channel.guild.id)}

            await self._node._send_payload(op, data=data)

        try:
            del self._node._players[self.channel.guild.id]
        except KeyError:
            pass

        self.cleanup()

    #

    async def play(
        self,
        track: Track[ContextT], /,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        no_replace: bool = False
    ) -> None:

        data: dict[str, Any] = {
            "track": track.id,
        }

        if self._node._type is NodeType.OBSIDIAN:
            op = 6
            data["guild_id"] = str(self.voice_channel.guild.id)
            if start_time:
                data["start_time"] = start_time
            if end_time:
                data["end_time"] = end_time
            if no_replace:
                data["no_replace"] = no_replace
        else:
            op = "play"
            data["guildId"] = str(self.voice_channel.guild.id)
            if start_time:
                data["startTime"] = start_time
            if end_time:
                data["endTime"] = end_time
            if no_replace:
                data["noReplace"] = no_replace

        await self._node._send_payload(op, data=data)
        __log__.info(f"Player '{self.voice_channel.guild.id}' started playing track '{track!r}'.")

        self._current_track_id = track.id
        self._current = track
        self._last_update = 0
        self._position = 0

    async def stop(
        self,
        *,
        force: bool = False
    ) -> None:

        if self._current is None and not force:
            return

        if self._node._type is NodeType.OBSIDIAN:
            op = 7
            data = {"guild_id": str(self.voice_channel.guild.id)}
        else:
            op = "stop"
            data = {"guildId": str(self.voice_channel.guild.id)}

        await self._node._send_payload(op, data=data)
        __log__.info(f"Player '{self.channel.guild.id}' stopped playing track '{self.current!r}'.")

        self._current_track_id = None
        self._current = None
        self._last_update = 0
        self._position = 0

    async def set_pause(
        self,
        pause: bool, /,
    ) -> None:

        if self._node._type is NodeType.OBSIDIAN:
            op = 8
            data = {"guild_id": str(self.voice_channel.guild.id), "state": pause}
        else:
            op = "pause"
            data = {"guildId": str(self.voice_channel.guild.id), "pause": pause}

        await self._node._send_payload(op, data=data)
        __log__.info(f"Player '{self.channel.guild.id}' set its paused state to '{pause}'.")

        self._paused = pause

    async def set_filter(
        self,
        filter: Filter,
        /,
        *,
        seek: bool = True
    ) -> None:

        if self._node._type is NodeType.OBSIDIAN:
            op = 9
            data = {"guild_id": str(self.voice_channel.guild.id), "filters": {**filter._payload}}
        else:
            op = "filters"
            data = {"guildId": str(self.voice_channel.guild.id), **filter._payload}

        await self._node._send_payload(op, data=data)
        __log__.info(f"Player '{self.channel.guild.id}' set its filter to '{filter!r}'.")

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

        if self._node._type is NodeType.OBSIDIAN:
            op = 10
            data = {"guild_id": str(self.voice_channel.guild.id), "position": round(position)}
        else:
            op = "seek"
            data = {"guildId": str(self.voice_channel.guild.id), "position": round(position)}

        await self._node._send_payload(op, data=data)
        __log__.info(f"Player '{self.channel.guild.id}' set its position to '{self.position}'.")

        self._last_update = time.time() * 1000
        self._position = position
