from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any, Generic, TypeAlias
import json as _json

import discord
import discord.types.voice
from typing_extensions import Self, TypeVar

from . import NodeNotReady
from .node import Node
from .objects.events import TrackEndEvent, TrackExceptionEvent, TrackStartEvent, TrackStuckEvent, WebsocketClosedEvent
from .types.common import VoiceChannel
from .types.objects.events import EventPayload


__all__: list[str] = ["Player"]
__log__: logging.Logger = logging.getLogger("discord-ext-lava.player")

ClientT = TypeVar("ClientT", bound=discord.Client | discord.AutoShardedClient, default=discord.Client)
Event: TypeAlias = TrackStartEvent | TrackEndEvent | TrackExceptionEvent | TrackStuckEvent | WebsocketClosedEvent


class Player(discord.VoiceProtocol, Generic[ClientT]):

    def __init__(self, *, node: Node) -> None:
        self.client: ClientT = discord.utils.MISSING
        self.channel: VoiceChannel = discord.utils.MISSING

        self._node: Node = node

        self._voice_state: dict[str, Any] = {}

    def __call__(self, client: discord.Client, channel: discord.abc.Connectable, /) -> Self:
        self.client = client  # type: ignore
        self.channel = channel  # type: ignore
        return self

    def __repr__(self) -> str:
        return "<discord.ext.lava.Player>"

    # properties

    @property
    def bot(self) -> ClientT:
        return self.client

    @property
    def guild(self) -> discord.Guild:
        return self.channel.guild

    @property
    def node(self) -> Node:
        return self._node

    # events

    _EVENT_MAPPING: Mapping[str, tuple[str, type[Event]]] = {
        "TrackStartEvent":      ("track_start", TrackStartEvent),
        "TrackEndEvent":        ("track_end", TrackEndEvent),
        "TrackExceptionEvent":  ("track_exception", TrackExceptionEvent),
        "TrackStuckEvent":      ("track_stuck", TrackStuckEvent),
        "WebSocketClosedEvent": ("web_socket_closed", WebsocketClosedEvent),
    }

    async def _handle_event(self, payload: EventPayload, /) -> None:

        event_type = payload["type"]

        if event := self._EVENT_MAPPING.get(event_type):
            dispatch_name, event = event
            event = event(payload)  # pyright: ignore - payload type can't be narrowed correctly
        else:
            dispatch_name, event = event_type, payload

        self.client.dispatch(f"lava_{dispatch_name}", event)
        __log__.info(f"Player for '{self.guild.name}' ({self.guild.id}) dispatched a '{event_type}' event to 'on_lava_{dispatch_name}' listeners.")

    # abcs

    async def on_voice_server_update(self, data: discord.types.voice.VoiceServerUpdate, /) -> None:
        __log__.debug(f"Player for '{self.guild.name}' ({self.guild.id}) received VOICE_SERVER_UPDATE.\n{_json.dumps(data, indent=4)}")
        self._voice_state["token"] = data["token"]
        self._voice_state["endpoint"] = data["endpoint"]
        await self._update_player()

    async def on_voice_state_update(self, data: discord.types.voice.GuildVoiceState, /) -> None:
        __log__.debug(f"Player for '{self.guild.name}' ({self.guild.id}) received VOICE_STATE_UPDATE.\n{_json.dumps(data, indent=4)}")
        self._voice_state["sessionId"] = data["session_id"]
        await self._update_player()

    async def connect(
        self, *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_deaf: bool = False,
        self_mute: bool = True,
    ) -> None:
        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)
        __log__.info(f"Player for '{self.guild.name}' ({self.guild.id}) connected to voice channel '{self.channel.name}' ({self.channel.id}).")

    async def disconnect(
        self, *,
        force: bool = False
    ) -> None:
        pass

    # rest api

    async def _update_player(self) -> None:

        if self.node.is_ready() is False:
            raise NodeNotReady(f"Node '{self.node.identifier}' is not ready.")

        data = {}
        if all(key in self._voice_state for key in ["token", "endpoint", "sessionId"]):
            data["voice"] = self._voice_state

        await self._node._request(
            "PATCH", f"sessions/{self.node._session_id}/players/{self.guild.id}",
            json=data
        )
