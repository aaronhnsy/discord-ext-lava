"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import abc
import logging
from typing import Any, Generic, Optional, TypeVar, Union

import discord
from discord.ext import commands


__all__ = ['BasePlayer']
__log__ = logging.getLogger('slate.player')


BotT = TypeVar('BotT', bound=Union[discord.Client, commands.Bot, commands.AutoShardedBot])


class BasePlayer(discord.VoiceProtocol, Generic[BotT], abc.ABC):

    def __init__(self, client: BotT, channel: discord.VoiceChannel) -> None:
        super().__init__(client, channel)

        self.client: BotT = client
        self.channel: Optional[discord.VoiceChannel] = channel

        self._bot: BotT = client
        self._guild: discord.Guild = channel.guild

    def __repr__(self) -> str:
        return f'<slate.BasePlayer>'

    @property
    def bot(self) -> BotT:
        return self._bot

    @property
    def guild(self) -> discord.Guild:
        return self._guild

    #

    def is_connected(self) -> bool:
        return self.channel is not None

    #

    @property
    @abc.abstractmethod
    def node(self) -> ...:
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
    async def move_to(self, channel: discord.VoiceChannel) -> None:
        raise NotImplementedError
