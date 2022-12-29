import json as _json
import logging
from collections.abc import Mapping
from typing import Generic

import discord
import discord.types.voice
from typing_extensions import Self, TypeVar

from .link import Link
from .objects.events import (
    Event, TrackEndEvent, TrackExceptionEvent, TrackStartEvent, TrackStuckEvent,
    WebSocketClosedEvent,
)
from .objects.types.events import EventData
from .types.common import VoiceChannel
from .types.rest.requests import UpdatePlayerData
from .types.websocket import PlayerUpdateData


__all__ = ["Player"]
__log__ = logging.getLogger("discord-ext-lava.player")

ClientT = TypeVar("ClientT", bound=discord.Client | discord.AutoShardedClient, default=discord.Client, covariant=True)


class Player(discord.VoiceProtocol, Generic[ClientT]):

    def __init__(self, *, link: Link) -> None:
        self.client: ClientT = discord.utils.MISSING
        self.channel: VoiceChannel = discord.utils.MISSING

        self._token: str | None = None
        self._endpoint: str | None = None
        self._session_id: str | None = None

        self._link: Link = link

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

    # websocket payload handlers

    _EVENT_MAPPING: Mapping[str, tuple[str, type[Event]]] = {
        "TrackStartEvent":      ("track_start", TrackStartEvent),
        "TrackEndEvent":        ("track_end", TrackEndEvent),
        "TrackExceptionEvent":  ("track_exception", TrackExceptionEvent),
        "TrackStuckEvent":      ("track_stuck", TrackStuckEvent),
        "WebSocketClosedEvent": ("web_socket_closed", WebSocketClosedEvent),
    }

    async def _handle_event_payload(self, payload: EventData, /) -> None:

        event_type = payload["type"]

        if event := self._EVENT_MAPPING.get(event_type):
            dispatch_name, event = event
            event = event(payload)  # pyright: ignore
        else:
            dispatch_name, event = event_type, payload

        self.client.dispatch(f"lava_{dispatch_name}", event, self)
        __log__.info(
            f"Player for '{self.guild.name}' ({self.guild.id}) dispatched a '{event_type}' event to "
            f"'on_lava_{dispatch_name}' listeners."
        )

    async def _handle_player_update_payload(self, payload: PlayerUpdateData, /) -> None:
        ...

    # rest api

    async def _update_player(self, data: UpdatePlayerData, /) -> None:

        if not self._link.is_ready():
            await self._link._ready_event.wait()

        await self._link._request(
            "PATCH", f"/sessions/{self._link.session_id}/players/{self.guild.id}",
            data=data
        )

    # voice state

    async def _update_voice_state(self) -> None:

        if self._token is None or self._endpoint is None or self._session_id is None:
            return

        await self._update_player(
            {"voice": {"token": self._token, "endpoint": self._endpoint, "sessionId": self._session_id}}
        )

    async def on_voice_server_update(self, data: discord.types.voice.VoiceServerUpdate, /) -> None:
        __log__.debug(
            f"Player for '{self.guild.name}' ({self.guild.id}) received VOICE_SERVER_UPDATE.\n"
            f"{_json.dumps(data, indent=4)}"
        )
        self._token = data["token"]
        self._endpoint = data["endpoint"]
        await self._update_voice_state()

    async def on_voice_state_update(self, data: discord.types.voice.GuildVoiceState, /) -> None:
        __log__.debug(
            f"Player for '{self.guild.name}' ({self.guild.id}) received VOICE_STATE_UPDATE.\n"
            f"{_json.dumps(data, indent=4)}"
        )

        if (channel_id := data["channel_id"]) is None:
            del self._link._players[self.guild.id]
            return
        self.channel = self.client.get_channel(int(channel_id))  # pyright: ignore

        self._session_id = data["session_id"]
        await self._update_voice_state()

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
