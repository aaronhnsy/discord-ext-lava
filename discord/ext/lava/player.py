import json
import logging
from typing import Generic, Self
from typing_extensions import TypeVar

import discord  # type: ignore
import discord.types.voice

from ._utilities import MISSING, DeferredMessage, get_event_dispatch_name
from .link import Link
from .objects.events import TrackEndEvent, TrackExceptionEvent, TrackStartEvent, TrackStuckEvent
from .objects.events import UnhandledEvent, WebSocketClosedEvent
from .objects.filters import Filter
from .objects.track import Track
from .types.common import PlayerStateData, VoiceChannel
from .types.objects.events import EventMapping
from .types.objects.track import TrackUserData
from .types.rest import PlayerData, UpdatePlayerRequestData, UpdatePlayerRequestParameters
from .types.rest import UpdatePlayerRequestTrackData, VoiceStateData
from .types.websocket import EventPayload


__all__ = ["Player"]
__log__: logging.Logger = logging.getLogger("discord.ext.lava.player")

ClientT = TypeVar("ClientT", bound=discord.Client, default=discord.Client, covariant=True)


class Player(discord.VoiceProtocol, Generic[ClientT]):

    def __init__(self, *, link: Link) -> None:
        self.client: ClientT = MISSING  # pyright: ignore
        self.channel: VoiceChannel = MISSING  # pyright: ignore
        self._link: Link = link
        # voice state
        self._token: str | None = None
        self._endpoint: str | None = None
        self._session_id: str | None = None
        # player state
        self._time: int = 0
        self._ping: int = -1
        self._connected: bool = False
        self._paused = False
        self._position: int = 0
        self._filter = Filter()
        self._volume = 100

    def __call__(self, client: discord.Client, channel: discord.abc.Connectable, /) -> Self:
        self.client = client  # pyright: ignore
        self.channel = channel  # pyright: ignore
        self._link._players[self.guild.id] = self
        return self

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Player: >"

    # voice state

    async def on_voice_server_update(self, data: discord.types.voice.VoiceServerUpdate, /) -> None:
        __log__.debug(
            f"Player for '{self.guild.name}' ({self.guild.id}) received VOICE_SERVER_UPDATE.\n%s",
            DeferredMessage(json.dumps, data, indent=4),
        )
        self._token = data["token"]
        self._endpoint = data["endpoint"]
        await self._update_voice_state()

    async def on_voice_state_update(self, data: discord.types.voice.GuildVoiceState, /) -> None:
        __log__.debug(
            f"Player for '{self.guild.name}' ({self.guild.id}) received VOICE_STATE_UPDATE.\n%s",
            DeferredMessage(json.dumps, data, indent=4),
        )
        # TODO: check if this is needed?
        # if (channel_id := data["channel_id"]) is None:
        #     del self._link._players[self.guild.id]
        #     return
        # self.channel = self.client.get_channel(int(channel_id))
        self._session_id = data["session_id"]
        await self._update_voice_state()

    async def _update_voice_state(self) -> None:
        if self._token is None or self._endpoint is None or self._session_id is None:
            return
        await self.update(
            voice_state={
                "token":     self._token,
                "endpoint":  self._endpoint,
                "sessionId": self._session_id
            }
        )

    # player state

    EVENT_MAPPING: EventMapping = {
        "TrackStartEvent":      TrackStartEvent,
        "TrackEndEvent":        TrackEndEvent,
        "TrackExceptionEvent":  TrackExceptionEvent,
        "TrackStuckEvent":      TrackStuckEvent,
        "WebSocketClosedEvent": WebSocketClosedEvent,
    }

    def _dispatch_event(self, payload: EventPayload, /) -> None:
        event = self.EVENT_MAPPING.get(payload["type"], UnhandledEvent)(payload)
        event_name = get_event_dispatch_name(event.type)
        self.client.dispatch(event_name, self, event)
        __log__.info(
            f"Player for '{self.guild.name}' ({self.guild.id}) dispatched '{event}' event to "
            f"'on_{event_name}' listeners."
        )

    def _update_player_state(self, payload: PlayerStateData, /) -> None:
        self._time = payload["time"]
        self._ping = payload["ping"]
        self._connected = payload["connected"]
        self._position = payload["position"]

    # TODO: split the update method into multiple methods, or something, idk.

    async def update(
        self,
        *,
        track: Track | None = MISSING,
        track_identifier: str = MISSING,
        track_user_data: TrackUserData = MISSING,
        track_end_time: int = MISSING,
        replace_current_track: bool = MISSING,
        paused: bool = MISSING,
        position: int = MISSING,
        filter: Filter = MISSING,
        volume: int = MISSING,
        voice_state: VoiceStateData = MISSING,
    ) -> None:
        if not self._link.is_ready():
            await self._link._ready_event.wait()
        if track is not None and track_identifier is not MISSING:
            raise ValueError("'track' and 'track_identifier' can not be used at the same time.")
        # parameters
        parameters: UpdatePlayerRequestParameters = {}
        if replace_current_track is not MISSING:
            parameters["noReplace"] = not replace_current_track
        # track data
        track_data: UpdatePlayerRequestTrackData = {}
        if track is not MISSING:
            track_data["encoded"] = track.encoded if track is not None else None
        if track_identifier is not MISSING:
            track_data["identifier"] = track_identifier
        if track_user_data is not MISSING:
            track_data["userData"] = track_user_data
        # data
        data: UpdatePlayerRequestData = {
            "track": track_data,
        }
        # track end time
        if track_end_time is not MISSING:
            if not isinstance(track_end_time, int):
                raise TypeError("'track_end_time' must be an integer.")
            data["endTime"] = track_end_time
        # pause state
        if paused is not MISSING:
            if not isinstance(paused, bool):
                raise TypeError("'paused' must be a boolean value.")
            data["paused"] = paused
        # position
        if position is not MISSING:
            if not isinstance(position, int):
                raise TypeError("'position' must be an integer.")
            data["position"] = position
        # filter
        if filter is not MISSING:
            if not isinstance(filter, Filter):
                raise TypeError("'filter' must be an instance of 'lava.Filter'.")
            data["filters"] = filter.data
        # volume
        if volume is not MISSING:
            if not isinstance(volume, int) or not 0 <= volume <= 1000:
                raise TypeError("'volume' must be an integer between '0' and '1000'.")
            data["volume"] = volume
        # voice state
        if voice_state is not MISSING:
            data["voice"] = voice_state
        # send request
        player: PlayerData = await self._link._request(
            "PATCH", f"/v4/sessions/{self._link.session_id}/players/{self.guild.id}",
            parameters=parameters, data=data,
        )
        self._update_player_state(player["state"])

    # properties

    @property
    def guild(self) -> discord.Guild:
        return self.channel.guild

    @property
    def time(self) -> int:
        return self._time

    @property
    def ping(self) -> int:
        return self._ping

    # connection state

    def is_connected(self) -> bool:
        return self._connected

    async def connect(
        self, *,
        self_mute: bool = False,
        self_deaf: bool = False,
        timeout: float | None = None,
        reconnect: bool | None = None,
    ) -> None:
        await self.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)
        __log__.info(
            f"Player for '{self.guild.name}' ({self.guild.id}) connected to voice channel "
            f"'{self.channel.name}' ({self.channel.id})."
        )

    async def move_to(self) -> None:
        raise NotImplementedError

    async def disconnect(self, *, force: bool = False) -> None:
        channel = self.channel
        await channel.guild.change_voice_state(channel=None)
        __log__.info(
            f"Player for '{channel.guild.name}' ({channel.guild.id}) disconnected from voice channel "
            f"'{channel.name}' ({channel.id})."
        )
        self.cleanup()
        del self._link._players[channel.guild.id]

    # pause state

    def is_paused(self) -> bool:
        return self._paused

    async def pause(self) -> None:
        await self.update(paused=True)

    async def set_pause_state(self, state: bool, /) -> None:
        await self.update(paused=state)

    async def resume(self) -> None:
        await self.update(paused=False)

    # position

    @property
    def position(self) -> int:
        return self._position

    async def set_position(self, position: int, /) -> None:
        await self.update(position=position)

    # filter

    @property
    def filter(self) -> Filter:
        return self._filter

    async def set_filter(self, filter: Filter, /) -> None:
        await self.update(filter=filter)

    # volume

    @property
    def volume(self) -> int:
        return self._volume

    async def set_volume(self, volume: int, /) -> None:
        await self.update(volume=volume)
