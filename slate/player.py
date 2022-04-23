# Future
from __future__ import annotations

# Standard Library
import logging
import time
from typing import Any, Generic

# Packages
import discord
import discord.types.voice
from typing_extensions import Self

# Local
from .node import Node
from .objects.enums import Provider
from .objects.events import TrackEnd, TrackException, TrackStart, TrackStuck, WebsocketClosed, WebsocketOpen
from .objects.filters import Filter
from .objects.track import Track
from .types import BotT, ContextT, PlayerT, VoiceChannel
from .utils import MISSING


__all__ = (
    "Player",
)
__log__: logging.Logger = logging.getLogger("slate.player")


OBSIDIAN_EVENT_MAPPING: dict[str, Any] = {
    "WEBSOCKET_OPEN":   WebsocketOpen,
    "WEBSOCKET_CLOSED": WebsocketClosed,
    "TRACK_START":      TrackStart,
    "TRACK_END":        TrackEnd,
    "TRACK_STUCK":      TrackStuck,
    "TRACK_EXCEPTION":  TrackException,
}

LAVALINK_EVENT_MAPPING: dict[str, Any] = {
    "WebsocketClosedEvent": WebsocketClosed,
    "TrackStartEvent":      TrackStart,
    "TrackEndEvent":        TrackEnd,
    "TrackStuckEvent":      TrackStuck,
    "TrackExceptionEvent":  TrackException,
}


class Player(discord.VoiceProtocol, Generic[BotT, ContextT, PlayerT]):

    def __call__(
        self,
        client: discord.Client,
        channel: discord.abc.Connectable,
    ) -> Self:

        self.client = client
        self.channel = channel  # type: ignore

        self._node._players[channel.guild.id] = self  # type: ignore

        return self

    def __init__(
        self,
        client: BotT = MISSING,
        channel: VoiceChannel = MISSING,
        *,
        node: Node[BotT, ContextT, PlayerT]
    ) -> None:

        self.client: BotT = client
        self.channel: VoiceChannel = channel

        self._node: Node[BotT, ContextT, PlayerT] = node

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

    # Discord.py abstract methods

    async def on_voice_server_update(
        self,
        data: discord.types.voice.VoiceServerUpdate
    ) -> None:

        __log__.debug(f"Player '{self.channel.guild.id}' received VOICE_SERVER_UPDATE.\nData: {data}")

        self._voice_server_update_data = data
        await self._dispatch_voice_update()

    async def on_voice_state_update(
        self,
        data: discord.types.voice.GuildVoiceState
    ) -> None:

        __log__.debug(f"Player '{self.channel.guild.id}' received VOICE_STATE_UPDATE.\nData: {data}")

        self._session_id = data.get("session_id")
        await self._dispatch_voice_update()

    async def _dispatch_voice_update(self) -> None:

        if not self._session_id or not self._voice_server_update_data:
            return

        if self._node.provider is Provider.OBSIDIAN:
            data = {
                "session_id": self._session_id,
                **self._voice_server_update_data
            }
        else:
            data = {
                "sessionId": self._session_id,
                "event":     self._voice_server_update_data,
            }

        await self._node._send_payload(
            0,  # voiceUpdate
            data=data,
            guild_id=str(self.channel.guild.id)
        )

    # Websocket

    def _dispatch_event(
        self,
        data: dict[str, Any]
    ) -> None:

        _type = data["type"]

        if not (event := OBSIDIAN_EVENT_MAPPING.get(_type) if self._node.provider is Provider.OBSIDIAN else LAVALINK_EVENT_MAPPING.get(_type)):
            __log__.error(f"Player '{self.channel.guild.id}' received an event with an unknown type '{_type}'.\nData: {data}")
            return

        event = event(data)

        __log__.info(f"Player '{self.channel.guild.id}' dispatched an event with type '{_type}'.\nData: {data}")
        self.bot.dispatch(f"slate_{event.type.lower()}", self, event)

    def _update_state(
        self,
        data: dict[str, Any]
    ) -> None:

        self._last_update = time.time() * 1000

        if self._node.provider is Provider.OBSIDIAN:

            current: dict[str, Any] = data["current_track"]
            self._current_track_id = current["track"]
            self._paused = current["paused"]
            self._position = current["position"]
            self._timestamp = data["timestamp"]
            # TODO: Parse filters from data["filters"]

        else:
            state: dict[str, Any] = data["state"]
            self._position = state.get("position", 0)
            self._timestamp = state["time"]

    # Properties

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
    def current_track_id(self) -> str | None:
        return self._current_track_id

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

    @property
    def listeners(self) -> list[discord.Member]:
        return [member for member in getattr(self.channel, "members", []) if not member.bot and (not member.voice.deaf or not member.voice.self_deaf)]

    # Utility methods

    def is_connected(self) -> bool:
        return self.channel is not None

    def is_playing(self) -> bool:
        return self.is_connected() is True and self._current is not None

    def is_paused(self) -> bool:
        return self._paused is True

    # Player methods

    async def connect(
        self,
        *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_mute: bool = False,
        self_deaf: bool = True,
    ) -> None:

        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)
        __log__.info(f"Player '{self.channel.guild.id}' connected to voice channel '{self.channel.id}'.")

    async def disconnect(
        self,
        *,
        force: bool = False
    ) -> None:

        __log__.info(f"Player '{self.channel.guild.id}' disconnected from voice channel '{self.channel.id}'.")
        await self.channel.guild.change_voice_state(channel=None)

        if self._node.is_connected():

            await self.stop(force=force)
            await self._node._send_payload(
                11,  # destroy
                guild_id=str(self.channel.guild.id)
            )

        try:
            del self._node._players[self.channel.guild.id]
        except KeyError:
            pass

        self.cleanup()

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
        if self._node.provider is Provider.OBSIDIAN:
            if start_time:
                data["start_time"] = start_time
            if end_time:
                data["end_time"] = end_time
            if no_replace:
                data["no_replace"] = no_replace
        else:
            if start_time:
                data["startTime"] = start_time
            if end_time:
                data["endTime"] = end_time
            if no_replace:
                data["noReplace"] = no_replace

        await self._node._send_payload(
            6,  # play
            data=data,
            guild_id=str(self.channel.guild.id)
        )
        __log__.info(f"Player '{self.channel.guild.id}' started playing track '{track!r}'.")

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

        await self._node._send_payload(
            7,  # stop
            guild_id=str(self.channel.guild.id)
        )
        __log__.info(f"Player '{self.channel.guild.id}' stopped playing track '{self.current!r}'.")

        self._current_track_id = None
        self._current = None
        self._last_update = 0
        self._position = 0

    async def set_pause(
        self,
        pause: bool, /,
    ) -> None:

        await self._node._send_payload(
            8,  # pause
            data={"state": pause} if self._node.provider is Provider.OBSIDIAN else {"pause": pause},
            guild_id=str(self.channel.guild.id)
        )
        __log__.info(f"Player '{self.channel.guild.id}' set its paused state to '{pause}'.")

        self._paused = pause

    async def set_filter(
        self,
        filter: Filter, /,
        *,
        set_position: bool = True
    ) -> None:

        await self._node._send_payload(
            9,  # filters
            data={"filters": filter._payload} if self._node.provider is Provider.OBSIDIAN else filter._payload,
            guild_id=str(self.channel.guild.id)
        )
        __log__.info(f"Player '{self.channel.guild.id}' set its filter to '{filter!r}'.")

        self._filter = filter

        if set_position:
            await self.set_position(self.position)

    async def set_position(
        self,
        position: float, /,
        *,
        force: bool = False
    ) -> None:

        if (self._current is None or 0 > position > self._current.length) and not force:
            return

        await self._node._send_payload(
            10,  # seek
            data={"position": round(position)},
            guild_id=str(self.channel.guild.id)
        )
        __log__.info(f"Player '{self.channel.guild.id}' set its position to '{self.position}'.")

        self._last_update = time.time() * 1000
        self._position = position
