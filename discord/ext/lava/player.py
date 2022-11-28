from __future__ import annotations

import logging
from typing import Generic

import discord
from discord.types.voice import GuildVoiceState, VoiceServerUpdate
from typing_extensions import Self

from ._types import ClientT, EventHandler
from .node import Node


__all__ = (
    "Player",
)


LOGGER: logging.Logger = logging.getLogger("discord-ext-lava.player")


class Player(discord.VoiceProtocol, Generic[ClientT]):

    def __init__(self, *, node: Node) -> None:
        self.client: ClientT = discord.utils.MISSING
        self.channel: discord.abc.Connectable = discord.utils.MISSING

        self._event_handlers: dict[str, EventHandler | None] = {}

        self._node: Node = node

    def __call__(self, client: ClientT, channel: discord.abc.Connectable, /) -> Self:
        self.client = client
        self.channel = channel
        return self

    def __repr__(self) -> str:
        return "<discord.ext.lava.Player>"

    # properties

    @property
    def node(self) -> Node:
        return self._node

    # events

    """

    @classmethod
    def event_handler(cls, name: str | None = None) -> Callable[[EventHandler], EventHandler]:

        def decorator(function: EventHandler) -> EventHandler:
            if isinstance(function, staticmethod):
                function = function.__func__
                
    """

    async def on_voice_server_update(self, data: VoiceServerUpdate, /) -> None:
        raise NotImplementedError

    async def on_voice_state_update(self, data: GuildVoiceState, /) -> None:
        raise NotImplementedError

    # methods

    async def connect(
        self, *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_deaf: bool = False,
        self_mute: bool = True,
    ) -> None:
        raise NotImplementedError

    async def disconnect(
        self, *,
        force: bool = False
    ) -> None:
        raise NotImplementedError
