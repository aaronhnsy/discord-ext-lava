from __future__ import annotations

import logging
from typing import Generic, Mapping

import discord
from discord.types.voice import GuildVoiceState, VoiceServerUpdate
from typing_extensions import Self

from ._types import ClientT, EventPayload, VoiceChannel
from .node import Node
from .objects.events import TrackEndEvent, TrackExceptionEvent, TrackStartEvent, TrackStuckEvent, WebsocketClosedEvent


__all__ = (
    "Player",
)


LOGGER: logging.Logger = logging.getLogger("discord-ext-lava.player")


class Player(discord.VoiceProtocol, Generic[ClientT]):

    def __init__(self, *, node: Node) -> None:
        self.client: ClientT = discord.utils.MISSING
        self.channel: VoiceChannel = discord.utils.MISSING

        self._node: Node = node

        self._voice_server_update_data: VoiceServerUpdate | None = None
        self._session_id: str | None = None

    def __call__(self, client: ClientT, channel: discord.abc.Connectable, /) -> Self:
        self.client = client
        self.channel = channel  # type: ignore
        return self

    def __repr__(self) -> str:
        return "<discord.ext.lava.Player>"

    # properties

    @property
    def node(self) -> Node:
        return self._node

    @property
    def guild(self) -> discord.Guild:
        return self.channel.guild

    # events

    _EVENT_MAPPING: Mapping[
        str,
        tuple[str, type[TrackStartEvent | TrackEndEvent | TrackExceptionEvent | TrackStuckEvent | WebsocketClosedEvent]]
    ] = {
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
        LOGGER.info(f"Player '{self.guild.id}' dispatched a '{event_type}' event to 'on_lava_{dispatch_name}' listeners.")

    # abcs

    async def on_voice_server_update(self, data: VoiceServerUpdate, /) -> None:
        pass

    async def on_voice_state_update(self, data: GuildVoiceState, /) -> None:
        pass

    async def connect(
        self, *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_deaf: bool = False,
        self_mute: bool = True,
    ) -> None:
        pass

    async def disconnect(
        self, *,
        force: bool = False
    ) -> None:
        pass
