from __future__ import annotations

import abc
import logging
from typing import Any, Generic, Optional, TypeVar, Union

from discord import Client, Guild, Member, VoiceChannel, VoiceProtocol
from discord.ext.commands import AutoShardedBot, Bot


__all__ = ['BasePlayer']
__log__: logging.Logger = logging.getLogger('slate.player')

BotT = TypeVar('BotT', bound=Union[Client, Bot, AutoShardedBot])


class BasePlayer(VoiceProtocol, Generic[BotT], abc.ABC):

    def __init__(self, client: BotT, channel: VoiceChannel) -> None:
        super().__init__(client, channel)

        self.client: BotT = client
        self.channel: Optional[VoiceChannel] = channel

        self._bot: BotT = client
        self._guild: Guild = channel.guild

    def __repr__(self) -> str:
        return f'<slate.BasePlayer>'

    @property
    def bot(self) -> BotT:
        return self._bot

    @property
    def guild(self) -> Guild:
        return self._guild

    #

    def is_connected(self) -> bool:
        return self.channel is not None

    #

    @property
    def listeners(self) -> list[Member]:
        return [member for member in getattr(self.channel, 'members', []) if not member.bot and not member.voice.deaf or not member.voice.self_deaf]

    #

    @property
    @abc.abstractmethod
    def node(self) -> Any:
        raise NotImplementedError

    #

    @abc.abstractmethod
    async def on_voice_server_update(self, data: dict[str, Any]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def on_voice_state_update(self, data: dict[str, Any]) -> None:
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
    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def disconnect(self, *, force: bool = False) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def move_to(self, channel: VoiceChannel) -> None:
        raise NotImplementedError
