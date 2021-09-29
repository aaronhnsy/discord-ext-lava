# Future
from __future__ import annotations

# Standard Library
import abc
import logging
from typing import Any, Generic, TypeVar, Union

# Packages
import discord
import discord.types.voice
from discord.ext import commands


__all__ = (
    "BasePlayer",
)
__log__: logging.Logger = logging.getLogger("slate.player")


BotT = TypeVar("BotT", bound=Union[discord.Client, discord.AutoShardedClient, commands.Bot, commands.AutoShardedBot])


class BasePlayer(discord.VoiceProtocol, abc.ABC, Generic[BotT]):

    def __init__(
        self,
        client: BotT,
        channel: discord.VoiceChannel
    ) -> None:

        super().__init__(
            client,
            channel
        )

        self.client: BotT = client
        self.channel: discord.VoiceChannel = channel

    #

    @property
    def listeners(self) -> list[discord.Member]:
        return [member for member in getattr(self.channel, "members", []) if not member.bot and not member.voice.deaf or not member.voice.self_deaf]

    def is_connected(self) -> bool:
        return self.channel is not None

    #

    @abc.abstractmethod
    async def on_voice_server_update(self, data: discord.types.voice.VoiceServerUpdate) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def on_voice_state_update(self, data: discord.types.voice.GuildVoiceState) -> None:
        raise NotImplementedError

    #

    @abc.abstractmethod
    async def _dispatch_voice_update(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _dispatch_event(self, data: dict[str, Any]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _update_state(self, data: dict[str, Any]) -> None:
        raise NotImplementedError

    #

    @abc.abstractmethod
    async def connect(
        self,
        *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_deaf: bool = False
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def disconnect(
        self,
        *,
        force: bool = False,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def move_to(
        self,
        channel: discord.VoiceChannel,
        /,
    ) -> None:
        raise NotImplementedError
