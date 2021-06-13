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
import asyncio
import logging
from typing import Any, Callable, Generic, Optional, TypeVar, Union

import aiohttp
import discord
from discord.ext import commands

from .exceptions import NodeNotConnected


__all__ = ['BaseNode']
__log__ = logging.getLogger('slate.node')


BotT = TypeVar('BotT', bound=Union[discord.Client, commands.Bot, commands.AutoShardedBot])


class BaseNode(abc.ABC, Generic[BotT]):

    def __init__(self, bot: BotT, host: str, port: str, password: str, identifier: str, region: Optional[discord.VoiceRegion], **kwargs) -> None:

        self._bot: BotT = bot
        self._host: str = host
        self._port: str = port
        self._password: str = password
        self._identifier: str = identifier
        self._region: Optional[discord.VoiceRegion] = region

        self._dumps: Callable[..., str] = kwargs['dumps']
        self._session: aiohttp.ClientSession = kwargs.get('session') or aiohttp.ClientSession()

        self._websocket: Optional[aiohttp.ClientWebSocketResponse] = None
        self._task: Optional[asyncio.Task] = None

    def __repr__(self) -> str:
        return f'<slate.BaseNode>'

    @property
    def bot(self) -> BotT:
        return self._bot

    @property
    def host(self) -> str:
        return self._host

    @property
    def post(self) -> str:
        return self._port

    @property
    def password(self) -> str:
        return self._password

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def region(self) -> Optional[discord.VoiceRegion]:
        return self._region

    #

    @property
    def session(self) -> aiohttp.ClientSession:
        return self._session

    @property
    def websocket(self) -> Optional[aiohttp.ClientWebSocketResponse]:
        return self._websocket

    @property
    def task(self) -> Optional[asyncio.Task]:
        return self._task

    #

    def is_connected(self) -> bool:
        return self._websocket is not None and not self._websocket.closed

    #

    @property
    @abc.abstractmethod
    def players(self) -> ...:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def http_url(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def ws_url(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def headers(self) -> dict[str, Any]:
        raise NotImplementedError

    #

    @abc.abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def disconnect(self, *, force: bool = False) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def destroy(self, *, force: bool = False) -> None:
        raise NotImplementedError

    async def send(self, op, **data) -> None:

        if not self.is_connected():
            raise NodeNotConnected(f'Node \'{self.identifier}\' is not connected.')

        payload = {'op': op.value, 'd': data}
        await self._websocket.send_json(payload)

        __log__.debug(f'NODE | \'{self.identifier}\' node sent a {op!r} payload. | Payload: {payload}')

    #

    @abc.abstractmethod
    async def _listen(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def _handle_payload(self, op, data: dict[str, Any]) -> None:
        raise NotImplementedError
