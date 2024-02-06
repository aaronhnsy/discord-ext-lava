from __future__ import annotations

import json
import logging
from typing import Generic, NotRequired, TypedDict, Unpack, cast
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
from .types.objects.events import EventMapping
from .types.objects.track import TrackUserData
from .types.rest import PlayerData, UpdatePlayerRequestData, UpdatePlayerRequestParameters
from .types.rest import UpdatePlayerRequestTrackData
from .types.websocket import EventPayload


__all__ = ["Player"]
__log__: logging.Logger = logging.getLogger("lava.player")

type Client = discord.Client
type Guild = discord.Guild
type Connectable = discord.abc.Connectable
type VoiceStateUpdateData = discord.types.voice.GuildVoiceState
type VoiceServerUpdateData = discord.types.voice.VoiceServerUpdate

BotT = TypeVar("BotT", bound=Client, default=Client, covariant=True)


class PlayerUpdateParameters(TypedDict):
    track: NotRequired[Track | None]
    track_identifier: NotRequired[str]
    track_user_data: NotRequired[TrackUserData]
    track_end_time: NotRequired[int]
    replace_current_track: NotRequired[bool]
    filter: NotRequired[Filter]
    position: NotRequired[int]
    paused: NotRequired[bool]
    volume: NotRequired[int]


class Player(discord.VoiceProtocol, Generic[BotT]):

    def __init__(self, link: Link) -> None:
        self._bot: BotT = MISSING
        self._guild: Guild = MISSING
        self._channel: VoiceChannel | None = MISSING
        self._link: Link = link
        # voice state
        self._token: str | None = None
        self._endpoint: str | None = None
        self._session_id: str | None = None
        # player state
        self._connected: bool = False
        self._ping: int = -1
        self._time: int = -1
        self._track: Track | None = None
        self._filter = Filter()
        self._position: int = 0
        self._paused = False
        self._volume = 100
        self._self_deaf: bool = False

    def __call__(self, client: Client, channel: Connectable) -> Player:
        self._bot = client                          # type: ignore
        self._guild = channel.guild                 # type: ignore
        self._channel = channel                     # type: ignore
        self._link._players[self._guild.id] = self  # type: ignore
        return self

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Player>"

    # rest voice state updates

    async def on_voice_state_update(self, data: VoiceStateUpdateData, /) -> None:
        __log__.debug(
            f"Player ({self._guild.id} : {self._guild.name}) received a 'VOICE_STATE_UPDATE' from Discord.\n"
            f"%s", DeferredMessage(json.dumps, data, indent=4),
        )
        # set discord voice state data
        self._session_id = data["session_id"]
        await self._update_player_voice_state()
        # update player voice channel
        id: int | None = int(channel_id) if (channel_id := data["channel_id"]) else None  # type: ignore
        channel: VoiceChannel | None = self._guild.get_channel(id)  # type: ignore
        if self._channel == channel:
            return
        elif self._channel is not None and channel is None:
            __log__.info(
                f"Player ({self._guild.id} : {self._guild.name}) disconnected from voice channel "
                f"({self._channel.id} : {self._channel.name})."
            )
        elif self._channel is None and channel is not None:
            __log__.info(
                f"Player ({self._guild.id} : {self._guild.name}) connected to voice channel "
                f"({channel.id} : {channel.name})."
            )
        elif self._channel is not None and channel is not None:
            __log__.info(
                f"Player ({self._guild.id} : {self._guild.name}) moved from voice channel "
                f"({self._channel.id} : {self._channel.name}) to ({channel.id} : {channel.name})."
            )
        self._channel = channel

    async def on_voice_server_update(self, data: VoiceServerUpdateData, /) -> None:
        __log__.debug(
            f"Player ({self._guild.id} : {self._guild.name}) received a 'VOICE_SERVER_UPDATE' from Discord.\n"
            f"%s", DeferredMessage(json.dumps, data, indent=4),
        )
        # set discord voice state data
        self._token = data["token"]
        self._endpoint = data["endpoint"]
        await self._update_player_voice_state()

    async def _update_player_voice_state(self) -> None:
        # check if all the data required to update the player's voice state is available
        if self._token is None or self._endpoint is None or self._session_id is None:
            return
        # update the player's voice state
        await self._link._request(
            "PATCH", f"/v4/sessions/{self._link.session_id}/players/{self._guild.id}",
            data={"voice": {"token": self._token, "endpoint": self._endpoint, "sessionId": self._session_id}},
        )
        # reset the discord voice state data to disallow subsequent 'VOICE_STATE_UPDATE'
        # events from updating the player's voice state unnecessarily
        self._token, self._endpoint, self._session_id = None, None, None

    # websocket payload handlers

    EVENT_MAPPING: EventMapping = {
        "TrackStartEvent":      TrackStartEvent,
        "TrackEndEvent":        TrackEndEvent,
        "TrackExceptionEvent":  TrackExceptionEvent,
        "TrackStuckEvent":      TrackStuckEvent,
        "WebSocketClosedEvent": WebSocketClosedEvent,
    }

    def _handle_event(self, payload: EventPayload, /) -> None:
        event = self.EVENT_MAPPING.get(payload["type"], UnhandledEvent)(payload)
        self._bot.dispatch(get_event_dispatch_name(event.type), self, event)
        __log__.info(f"Player ({self._guild.id} : {self._guild.name}) dispatched {event}")

    def _handle_player_state_update(self, payload: PlayerStateData, /) -> None:
        self._connected = payload["connected"]
        self._ping = payload["ping"]
        self._time = payload["time"]
        self._position = payload["position"]

    def _update_player(self, data: PlayerData) -> None:
        self._handle_player_state_update(data["state"])
        self._track = Track(data["track"]) if data["track"] else None
        # self._filter = Filter(data["filters"]) ???
        self._volume = data["volume"]
        self._paused = data["paused"]

    # properties

    @property
    def channel(self) -> VoiceChannel | None:  # pyright: ignore
        return self._channel

    @property
    def time(self) -> int:
        return self._time

    @property
    def ping(self) -> int:
        return self._ping

    # methods

    async def update(self, **kwargs: Unpack[PlayerUpdateParameters]) -> None:
        # validate that track and track_identifier are not used at the same time
        track = kwargs.get("track", MISSING)
        track_identifier = kwargs.get("track_identifier")
        if track is not MISSING and track_identifier is not None:
            raise ValueError("'track' and 'track_identifier' can not be used at the same time.")

        # wait for the player to be ready
        if not self._link.is_ready():
            await self._link._ready_event.wait()

        # prepare request parameters
        parameters: UpdatePlayerRequestParameters = {}
        if replace_current_track := kwargs.get("replace_current_track"):
            parameters["noReplace"] = not replace_current_track

        # prepare request track data
        track_data: UpdatePlayerRequestTrackData = {}
        if track is not MISSING:
            track_data["encoded"] = track.encoded if track is not None else None
        if track_identifier:
            track_data["identifier"] = track_identifier
        if track_user_data := kwargs.get("track_user_data"):
            track_data["userData"] = track_user_data

        # prepare request data
        data: UpdatePlayerRequestData = {}
        if track_data:
            data["track"] = track_data
        if track_end_time := kwargs.get("track_end_time"):
            if not isinstance(track_end_time, int):
                raise TypeError("'track_end_time' must be an integer.")
            data["endTime"] = track_end_time
        if filter := kwargs.get("filter"):
            if not isinstance(filter, Filter):
                raise TypeError("'filter' must be an instance of 'lava.Filter'.")
            data["filters"] = filter.data
            self._filter = filter
        if position := kwargs.get("position"):
            if not isinstance(position, int):
                raise TypeError("'position' must be an integer.")
            data["position"] = position
        if paused := kwargs.get("paused"):
            if not isinstance(paused, bool):
                raise TypeError("'paused' must be a boolean value.")
            data["paused"] = paused
        if volume := kwargs.get("volume"):
            if not isinstance(volume, int) or not 0 <= volume <= 1000:
                raise TypeError("'volume' must be an integer between '0' and '1000'.")
            data["volume"] = volume

        # send request
        player: PlayerData = await self._link._request(
            "PATCH", f"/v4/sessions/{self._link.session_id}/players/{self._guild.id}",
            parameters=parameters, data=data,
        )
        self._update_player(player)

    # connection state

    def is_connected(self) -> bool:
        return self._channel is not None and self._connected is True

    async def connect(
        self, *,
        channel: VoiceChannel | None = None,
        timeout: float = 60.0,
        reconnect: bool = False,
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        if self.is_connected():
            raise PlayerAlreadyConnected("This player is already connected to a voice channel.")
        if self._channel is None and channel is None:
            raise ValueError("You must provide the 'channel' parameter to reconnect this player.")
        self._channel = cast(VoiceChannel, self._channel or channel)
        __log__.info(
            f"Player ({self._guild.id} : {self._guild.name}) connected to voice channel "
            f"({self._channel.id} : {self._channel.name})."
        )
        await self._guild.change_voice_state(channel=self._channel, self_deaf=self._self_deaf)

    async def move_to(self, channel: VoiceChannel, /) -> None:
        if not self.is_connected():
            raise PlayerNotConnected("This player is not connected to a voice channel.")
        self._channel = channel
        __log__.info(
            f"Player ({self._guild.id} : {self._guild.name}) moved from voice channel "
            f"({self._channel.id} : {self._channel.name}) to ({channel.id} : {channel.name})."
        )
        await self._guild.change_voice_state(channel=self._channel, self_deaf=self._self_deaf)

    async def disconnect(self, *, force: bool = False) -> None:
        if not self.is_connected():
            raise PlayerNotConnected("This player is not connected to a voice channel.")
        old_channel = cast(VoiceChannel, self._channel)
        self._channel = None
        __log__.info(
            f"Player ({self._guild.id} : {self._guild.name}) disconnected from voice channel "
            f"({old_channel.id} : {old_channel.name})."
        )
        await self._guild.change_voice_state(channel=self._channel, self_deaf=self._self_deaf)

    # TODO: play() and stop() methods for tracks

    # filter

    @property
    def filter(self) -> Filter:
        return self._filter

    async def set_filter(self, filter: Filter, /) -> None:
        await self.update(filter=filter)

    # position

    @property
    def position(self) -> int:
        return self._position

    async def set_position(self, position: int, /) -> None:
        await self.update(position=position)

    # paused

    def is_paused(self) -> bool:
        return self._paused

    async def pause(self) -> None:
        await self.update(paused=True)

    async def set_pause_state(self, state: bool, /) -> None:
        await self.update(paused=state)

    async def resume(self) -> None:
        await self.update(paused=False)

    # volume

    @property
    def volume(self) -> int:
        return self._volume

    async def set_volume(self, volume: int, /) -> None:
        await self.update(volume=volume)

    # self deaf

    def is_self_deaf(self) -> bool:
        return self._self_deaf

    async def set_self_deaf(self, state: bool, /) -> None:
        self._self_deaf = state
        await self._guild.change_voice_state(channel=self._channel, self_deaf=state)
