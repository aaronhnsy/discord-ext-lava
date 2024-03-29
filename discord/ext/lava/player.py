from __future__ import annotations

import json
import logging
import time
from typing import Generic, cast
from typing_extensions import TypeVar

import discord
import discord.types.voice

from ._utilities import MISSING, DeferredMessage, get_event_dispatch_name
from .exceptions import PlayerAlreadyConnected, PlayerNotConnected
from .link import Link
from .objects.events import TrackEndEvent, TrackExceptionEvent, TrackStartEvent, TrackStuckEvent
from .objects.events import UnhandledEvent, WebSocketClosedEvent
from .objects.filters import Filter
from .objects.track import Track
from .types.common import PlayerStateData, VoiceChannel
from .types.objects.track import TrackUserData
from .types.rest import PlayerData, UpdatePlayerRequestData, UpdatePlayerRequestParameters
from .types.rest import UpdatePlayerRequestTrackData
from .types.websocket import EventPayload


__all__ = ["Player"]
__log__: logging.Logger = logging.getLogger("lava.player")

BotT = TypeVar("BotT", bound=discord.Client, default=discord.Client, covariant=True)

type Connectable = discord.abc.Connectable
type VoiceStateUpdateData = discord.types.voice.GuildVoiceState
type VoiceServerUpdateData = discord.types.voice.VoiceServerUpdate


class Player(discord.VoiceProtocol, Generic[BotT]):

    def __init__(self, link: Link) -> None:
        self._bot: BotT = MISSING
        self._guild: discord.Guild = MISSING
        self._channel: VoiceChannel | None = MISSING
        self._link: Link = link
        # player voice state
        self._token: str | None = None
        self._endpoint: str | None = None
        self._session_id: str | None = None
        # player state
        self._connected: bool = False
        self._ping: int = -1
        self._position: int = 0
        self._time: int = 0
        # player data
        self._track: Track | None = None
        self._filter: Filter | None = None
        self._paused = False
        self._volume = 100

    def __call__(self, client: discord.Client, channel: Connectable) -> Player:
        self._bot = client                         # type: ignore
        self._guild = channel.guild                # type: ignore
        self._channel = channel                    # type: ignore
        self._link._players[self.guild.id] = self  # type: ignore
        return self

    def __repr__(self) -> str:
        return f"<lava.{self.__class__.__name__}: >"

    # properties

    @property
    def guild(self) -> discord.Guild:
        return self._guild

    @property
    def channel(self) -> VoiceChannel | None:  # pyright: ignore
        return self._channel

    @property
    def ping(self) -> int:
        return self._ping

    @property
    def time(self) -> int:
        return self._time

    # voice state update

    async def on_voice_state_update(self, data: VoiceStateUpdateData, /) -> None:
        __log__.debug(
            f"Player ({self.guild.id} : {self.guild.name}) received a 'VOICE_STATE_UPDATE' from Discord.\n"
            f"%s", DeferredMessage(json.dumps, data, indent=4),
        )
        # set discord voice state data
        self._session_id = data["session_id"]
        await self._update_voice_state()
        # update player voice channel
        id: int | None = int(channel_id) if (channel_id := data["channel_id"]) else None  # type: ignore
        channel: VoiceChannel | None = self.guild.get_channel(id)  # type: ignore
        if self._channel == channel:
            return
        elif self._channel is not None and channel is None:
            __log__.info(
                f"Player ({self.guild.id} : {self.guild.name}) disconnected from voice channel "
                f"({self._channel.id} : {self._channel.name})."
            )
        elif self._channel is None and channel is not None:
            __log__.info(
                f"Player ({self.guild.id} : {self.guild.name}) connected to voice channel "
                f"({channel.id} : {channel.name})."
            )
        elif self._channel is not None and channel is not None:
            __log__.info(
                f"Player ({self.guild.id} : {self.guild.name}) moved from voice channel "
                f"({self._channel.id} : {self._channel.name}) to ({channel.id} : {channel.name})."
            )
        self._channel = channel

    async def on_voice_server_update(self, data: VoiceServerUpdateData, /) -> None:
        __log__.debug(
            f"Player ({self.guild.id} : {self.guild.name}) received a 'VOICE_SERVER_UPDATE' from Discord.\n"
            f"%s", DeferredMessage(json.dumps, data, indent=4),
        )
        # set discord voice state data
        self._token = data["token"]
        self._endpoint = data["endpoint"]
        await self._update_voice_state()

    async def _update_voice_state(self) -> None:
        # check if all the data required to update the player's voice state is available
        if self._token is None or self._endpoint is None or self._session_id is None:
            return
        # update the player's voice state
        await self._link._request(
            "PATCH", f"/v4/sessions/{self._link.session_id}/players/{self.guild.id}",
            data={"voice": {"token": self._token, "endpoint": self._endpoint, "sessionId": self._session_id}},
        )
        # reset the discord voice state data to disallow subsequent 'VOICE_STATE_UPDATE'
        # events from updating the player's voice state unnecessarily
        self._token, self._endpoint, self._session_id = None, None, None

    # events + player updates

    def _dispatch_event(self, payload: EventPayload, /) -> None:
        match payload["type"]:
            case "TrackStartEvent":
                event = TrackStartEvent(payload)
            case "TrackEndEvent":
                event = TrackEndEvent(payload)
            case "TrackExceptionEvent":
                event = TrackExceptionEvent(payload)
            case "TrackStuckEvent":
                event = TrackStuckEvent(payload)
            case "WebSocketClosedEvent":
                event = WebSocketClosedEvent(payload)
            case _:  # pyright: ignore - lavalink could add new event types
                event = UnhandledEvent(payload)
        self._bot.dispatch(get_event_dispatch_name(event.type), self, event)
        __log__.info(f"Player ({self.guild.id} : {self.guild.name}) dispatched '{event}'")

    def _update_player_state(self, payload: PlayerStateData, /) -> None:
        self._connected = payload["connected"]
        self._ping = payload["ping"]
        self._position = payload["position"]
        self._time = payload["time"]

    def _update_player_data(self, data: PlayerData) -> None:
        self._update_player_state(data["state"])
        self._track = Track(data["track"]) if data["track"] else None
        # self._filter = Filter(data["filters"])
        self._volume = data["volume"]
        self._paused = data["paused"]

    # methods

    async def update(
        self,
        *,
        track: Track | None = MISSING,
        track_identifier: str = MISSING,
        track_user_data: TrackUserData = MISSING,
        track_end_time: int | None = MISSING,
        replace_current_track: bool = MISSING,
        filter: Filter = MISSING,
        position: int = MISSING,
        paused: bool = MISSING,
        volume: int = MISSING,
    ) -> None:
        # validate that track and track_identifier are not used at the same time
        if track is not MISSING and track_identifier is not MISSING:
            raise ValueError("'track' and 'track_identifier' can not be used at the same time.")
        # wait for the player to be ready
        if not self._link.is_ready():
            await self._link._ready_event.wait()

        # prepare request parameters
        parameters: UpdatePlayerRequestParameters = {}
        if replace_current_track is not MISSING:
            parameters["noReplace"] = not replace_current_track

        # prepare request track data
        track_data: UpdatePlayerRequestTrackData = {}
        if track is not MISSING:
            track_data["encoded"] = track.encoded if track else None
        if track_identifier is not MISSING:
            track_data["identifier"] = track_identifier
        if track_user_data is not MISSING:
            track_data["userData"] = track_user_data

        # prepare request data
        data: UpdatePlayerRequestData = {}
        if track_data:
            data["track"] = track_data
        if track_end_time is not MISSING:
            if isinstance(track_end_time, int) and track_end_time <= 0:
                raise TypeError("'track_end_time' must be an integer more than or equal to '1'.")
            data["endTime"] = track_end_time
        if filter is not MISSING:
            data["filters"] = filter.data
        if position is not MISSING:
            data["position"] = position
        if paused is not MISSING:
            data["paused"] = paused
        if volume is not MISSING:
            if volume < 0 or volume > 1000:
                raise TypeError("'volume' must be an integer between '0' and '1000' inclusive.")
            data["volume"] = volume

        # send request
        player: PlayerData = await self._link._request(
            "PATCH", f"/v4/sessions/{self._link.session_id}/players/{self.guild.id}",
            parameters=parameters, data=data,
        )
        self._update_player_data(player)

    # connection

    def is_connected(self) -> bool:
        return self._channel is not None and self._connected is True

    async def connect(
        self, *,
        channel: VoiceChannel | None = None,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_deaf: bool | None = None,
        self_mute: bool | None = None,
    ) -> None:
        if self.is_connected():
            raise PlayerAlreadyConnected("This player is already connected to a voice channel.")
        if self._channel is None and channel is None:
            raise ValueError("You must provide the 'channel' parameter to reconnect this player.")
        self._channel = cast(VoiceChannel, self._channel or channel)
        __log__.info(
            f"Player ({self.guild.id} : {self.guild.name}) connected to voice channel "
            f"({self._channel.id} : {self._channel.name})."
        )
        await self.guild.change_voice_state(channel=self._channel)

    async def move_to(self, channel: VoiceChannel) -> None:
        if not self.is_connected():
            raise PlayerNotConnected("This player is not connected to a voice channel.")
        self._channel = channel
        __log__.info(
            f"Player ({self.guild.id} : {self.guild.name}) moved from voice channel "
            f"({self._channel.id} : {self._channel.name}) to ({channel.id} : {channel.name})."
        )
        await self.guild.change_voice_state(channel=self._channel)

    async def disconnect(self, *, force: bool = False) -> None:
        if not self.is_connected():
            raise PlayerNotConnected("This player is not connected to a voice channel.")
        old_channel = cast(VoiceChannel, self._channel)
        self._channel = None
        __log__.info(
            f"Player ({self.guild.id} : {self.guild.name}) disconnected from voice channel "
            f"({old_channel.id} : {old_channel.name})."
        )
        await self.guild.change_voice_state(channel=self._channel)

    # position

    @property
    def position(self) -> int:
        return round(self._position + ((time.time() * 1000) - self._time))

    async def set_position(self, position: int, /) -> None:
        await self.update(position=position)
        __log__.info(f"Player ({self.guild.id} : {self.guild.name}) set it's position to '{self.position}'.")

    # track

    @property
    def track(self) -> Track | None:
        return self._track

    async def play(
        self,
        track: Track,
        /, *,
        end_time: int | None = None,
        replace_current_track: bool = True,
    ) -> None:
        await self.update(track=track, track_end_time=end_time, replace_current_track=replace_current_track)
        __log__.info(
            f"Player ({self.guild.id} : {self.guild.name}) started playing '{track.title}' by '{track.author}'."
        )

    async def stop(self) -> None:
        await self.update(track=None)
        __log__.info(f"Player ({self.guild.id} : {self.guild.name}) stopped playing.")

    # filter

    @property
    def filter(self) -> Filter | None:
        return self._filter

    async def set_filter(
        self,
        filter: Filter,
        /, *,
        instant: bool = True
    ) -> None:
        await self.update(filter=filter, position=self.position if instant else MISSING)
        __log__.info(f"Player ({self.guild.id} : {self.guild.name}) set it's filter to '{filter}'.")

    # paused

    def is_paused(self) -> bool:
        return self._paused

    async def pause(self) -> None:
        await self.set_pause_state(True)

    async def set_pause_state(self, state: bool, /) -> None:
        await self.update(paused=state)
        __log__.info(f"Player ({self.guild.id} : {self.guild.name}) set it's paused state to '{state}'.")

    async def resume(self) -> None:
        await self.set_pause_state(False)

    # volume

    @property
    def volume(self) -> int:
        return self._volume

    async def set_volume(self, volume: int, /) -> None:
        await self.update(volume=volume)
