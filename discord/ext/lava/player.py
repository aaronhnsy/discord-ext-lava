from typing import Generic

import discord
from discord.types.voice import (
    GuildVoiceState as VoiceStateUpdatePayload,
    VoiceServerUpdate as VoiceServerUpdatePayload,
)
from typing_extensions import Self

from ._types import ClientT
from .node import Node


__all__ = (
    "Player",
)


class Player(discord.VoiceProtocol, Generic[ClientT]):

    def __init__(self, *, node: Node) -> None:
        self.client: ClientT = discord.utils.MISSING
        self.channel: discord.abc.Connectable = discord.utils.MISSING

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

    # abstract base methods

    async def on_voice_server_update(self, data: VoiceServerUpdatePayload, /) -> None:
        raise NotImplementedError

    async def on_voice_state_update(self, data: VoiceStateUpdatePayload, /) -> None:
        raise NotImplementedError

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
