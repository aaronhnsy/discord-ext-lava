# Standard Library
import json
import logging
from typing import Generic, Self
from typing_extensions import TypeVar

# Libraries
import discord  # type: ignore
import discord.types.voice

# Local Folder
from ._utilities import MISSING, DeferredMessage
from .link import Link
from .objects.events import TrackEndEvent, TrackExceptionEvent, TrackStartEvent, TrackStuckEvent, WebSocketClosedEvent
from .objects.filters import Filter
from .objects.track import Track
from .types.common import VoiceChannel
from .types.objects.track import TrackUserData
from .types.rest import UpdatePlayerRequestData, UpdatePlayerRequestParameters, UpdatePlayerRequestTrackData
from .types.rest import VoiceStateData
from .types.websocket import EventPayload, PlayerUpdatePayload


__all__ = ["Player"]

__log__: logging.Logger = logging.getLogger("discord.ext.lava.player")

ClientT = TypeVar(
    "ClientT",
    bound=discord.Client | discord.AutoShardedClient,
    default=discord.Client,
    covariant=True
)


class Player(discord.VoiceProtocol, Generic[ClientT]):

    def __init__(self, *, link: Link) -> None:
        # player info
        self.client: ClientT = MISSING
        self.channel: VoiceChannel = MISSING
        self._link: Link = link
        # voice state
        self._token: str | None = None
        self._endpoint: str | None = None
        self._session_id: str | None = None
        # player state (websocket)
        self._time: int = 0
        self._position: int = 0
        self._connected: bool = False
        self._ping: int = -1
        # player state (http)
        self._paused = False
        self._volume = 100
        self._filter = Filter()

    def __call__(self, client: discord.Client, channel: discord.abc.Connectable, /) -> Self:
        self.client = client  # pyright: ignore
        self.channel = channel  # pyright: ignore
        self._link._players[self.guild.id] = self
        return self

    def __repr__(self) -> str:
        return "<discord.ext.lava.Player>"

    # properties

    @property
    def guild(self) -> discord.Guild:
        return self.channel.guild

    @property
    def ping(self) -> int:
        return self._ping

    @property
    def position(self) -> float:
        return self._position

    def is_connected(self) -> bool:
        return self._connected and self.channel is not None

    # websocket

    _EVENT_MAPPING = {
        "TrackStartEvent":      ("track_start", TrackStartEvent),
        "TrackEndEvent":        ("track_end", TrackEndEvent),
        "TrackExceptionEvent":  ("track_exception", TrackExceptionEvent),
        "TrackStuckEvent":      ("track_stuck", TrackStuckEvent),
        "WebSocketClosedEvent": ("web_socket_closed", WebSocketClosedEvent),
    }

    async def _handle_event(self, payload: EventPayload, /) -> None:
        event_type = payload["type"]
        if event_items := self._EVENT_MAPPING.get(event_type):
            dispatch_name, event_cls = event_items
            event = event_cls(payload)  # pyright: ignore
        else:
            dispatch_name, event = event_type, payload
        self.client.dispatch(f"lava_{dispatch_name}", event, self)
        __log__.info(
            f"Player for '{self.guild.name}' ({self.guild.id}) dispatched a '{event_type}' event to "
            f"'on_lava_{dispatch_name}' listeners."
        )

    async def _handle_player_update(self, payload: PlayerUpdatePayload, /) -> None:
        self._time = payload["state"]["time"]
        self._position = payload["state"]["position"]
        self._connected = payload["state"]["connected"]
        self._ping = payload["state"]["ping"]

    # voice state

    async def _update_player_voice_state(self) -> None:
        if self._token is None or self._endpoint is None or self._session_id is None:
            return
        await self.update(
            voice_state={
                "token":     self._token,
                "endpoint":  self._endpoint,
                "sessionId": self._session_id
            }
        )

    async def on_voice_server_update(self, data: discord.types.voice.VoiceServerUpdate, /) -> None:
        __log__.debug(
            f"Player for '{self.guild.name}' ({self.guild.id}) received VOICE_SERVER_UPDATE.\n%s",
            DeferredMessage(json.dumps, data, indent=4),
        )
        self._token = data["token"]
        self._endpoint = data["endpoint"]
        await self._update_player_voice_state()

    async def on_voice_state_update(self, data: discord.types.voice.GuildVoiceState, /) -> None:
        __log__.debug(
            f"Player for '{self.guild.name}' ({self.guild.id}) received VOICE_STATE_UPDATE.\n%s",
            DeferredMessage(json.dumps, data, indent=4),
        )
        """
        if (channel_id := data["channel_id"]) is None:
            del self._link._players[self.guild.id]
            return
        self.channel = self.client.get_channel(int(channel_id))
        """
        self._session_id = data["session_id"]
        await self._update_player_voice_state()

    # connection

    async def connect(
        self, *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        await self.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)
        __log__.info(
            f"Player for '{self.guild.name}' ({self.guild.id}) connected to voice channel "
            f"'{self.channel.name}' ({self.channel.id})."
        )

    async def disconnect(
        self, *,
        force: bool = False
    ) -> None:
        channel = self.channel
        await channel.guild.change_voice_state(channel=None)
        __log__.info(
            f"Player for '{channel.guild.name}' ({channel.guild.id}) disconnected from voice channel "
            f"'{channel.name}' ({channel.id})."
        )

    async def update(
        self,
        *,
        track: Track | None = MISSING,
        track_identifier: str = MISSING,
        track_user_data: TrackUserData = MISSING,
        track_end_time: int = MISSING,
        replace_current_track: bool = MISSING,
        position: int = MISSING,
        paused: bool = MISSING,
        volume: int = MISSING,
        filter: Filter = MISSING,
        voice_state: VoiceStateData = MISSING,
    ) -> None:
        if not self._link.is_ready():
            await self._link._ready_event.wait()
        if track is not None and track_identifier is not MISSING:
            raise ValueError("'track' and 'track_identifier' can not be used at the same time.")
        # request parameters
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
        # request data
        data: UpdatePlayerRequestData = {
            "track": track_data,
        }
        if track_end_time is not MISSING:
            data["endTime"] = track_end_time
        if position is not MISSING:
            data["position"] = position

        # paused
        if paused is not MISSING:
            if not isinstance(paused, bool):
                raise TypeError("'paused' must be a boolean value.")
            data["paused"] = paused
        # volume
        if volume is not MISSING:
            if not isinstance(volume, int) or not 0 <= volume <= 1000:
                raise TypeError("'volume' must be an integer between '0' and '1000'.")
            data["volume"] = volume
        # filters
        if filter is not MISSING:
            if not isinstance(filter, Filter):
                raise TypeError("'filter' must be an instance of 'lava.Filter'.")
            data["filters"] = filter.data
        # voice state
        if voice_state is not MISSING:
            data["voice"] = voice_state

        # send request
        await self._link._request(
            "PATCH", f"/v4/sessions/{self._link.session_id}/players/{self.guild.id}",
            parameters=parameters, data=data,
        )

        # set player state
        if "paused" in data:
            self._paused = data["paused"]
        if "volume" in data:
            self._volume = data["volume"]
        if "filters" in data:
            self._filter = filter

    # pausing

    def is_paused(self) -> bool:
        return self._paused

    async def pause(self) -> None:
        await self.update(paused=True)

    async def set_pause_state(self, state: bool) -> None:
        await self.update(paused=state)

    async def resume(self) -> None:
        await self.update(paused=False)

    # volume

    @property
    def volume(self) -> int:
        return self._volume

    async def set_volume(self, volume: int, /) -> None:
        await self.update(volume=volume)

    # filters

    @property
    def filter(self) -> Filter:
        return self._filter

    async def set_filter(self, filter: Filter, /) -> None:
        await self.update(filter=filter)
