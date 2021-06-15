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

import asyncio
import logging
from typing import Any, Generic, Optional, TypeVar, Union

import aiohttp
import discord
from discord.ext import commands

from ..node import BaseNode


__all__ = ['LavalinkNode']
__log__: logging.Logger = logging.getLogger('slate.obsidian.node')


BotT = TypeVar('BotT', bound=Union[discord.Client, commands.Bot, commands.AutoShardedBot])


class LavalinkNode(BaseNode, Generic[BotT]):

    def __init__(self, bot: BotT, host: str, port: str, password: str, identifier: str, region: Optional[discord.VoiceRegion], **kwargs) -> None:
        super().__init__(bot, host, port, password, identifier, region, **kwargs)

        self._players: list[ObsidianPlayer] = []

    def __repr__(self) -> str:
        return f'<slate.ObsidianNode>'

    #

    @property
    def players(self) -> list[ObsidianPlayer]:
        """
        :py:class:`Dict` [ :py:class:`int` , :py:class:`Player` ]:
            A mapping of player guild id's to players that this node is managing.
        """
        return self._players

    #

    @property
    def http_url(self) -> str:
        return f'http://{self._host}:{self._port}/'

    @property
    def ws_url(self) -> str:
        return f'ws://{self._host}:{self._port}/magma'

    @property
    def headers(self) -> dict[str, Any]:
        return {
            'Authorization': self._password,
            'User-Id': str(self._bot.bot.user.id),
            'Client-Name': 'Slate/0.1.0',
        }

    #

    async def connect(self) -> None:

        await self.bot.bot.wait_until_ready()

        try:
            websocket = await self.client.session.ws_connect(self._ws_url, headers=self._headers)

        except Exception as error:

            self._available = False

            if isinstance(error, aiohttp.WSServerHandshakeError) and error.status in (401, 4001):
                __log__.warning(f'NODE | \'{self.identifier}\' failed to connect due to invalid authorization.')
                raise NodeConnectionError(f'Node \'{self.identifier}\' failed to connect due to invalid authorization.')

            __log__.warning(f'NODE | \'{self.identifier}\' failed to connect. Error: {error}')
            raise NodeConnectionError(f'Node \'{self.identifier}\' failed to connect.\n{error}')

        else:

            self._available = True
            self._websocket = websocket

            if not self._task:
                self._task = asyncio.create_task(self._listen())

            self._client.nodes[self.identifier] = self
            __log__.info(f'NODE | \'{self.identifier}\' connected successfully.')

    async def reconnect(self) -> None:

        await self.client.bot.wait_until_ready()

        try:
            websocket = await self.client.session.ws_connect(self._ws_url, headers=self._headers)

        except Exception as error:

            self._available = False

            if isinstance(error, aiohttp.WSServerHandshakeError) and error.status in (401, 4001):
                __log__.warning(f'NODE | \'{self.identifier}\' failed to connect due to invalid authorization.')
            else:
                __log__.warning(f'NODE | \'{self.identifier}\' failed to connect. Error: {error}')

        else:

            self._available = True
            self._websocket = websocket

            if not self._task:
                self._task = asyncio.create_task(self._listen())

            self._client.nodes[self.identifier] = self
            __log__.info(f'NODE | \'{self.identifier}\' connected successfully.')

    async def disconnect(self, *, force: bool = False) -> None:


        for player in self._players.copy().values():
            await player.destroy(force=force)

        if self.is_connected:
            await self._websocket.close()
        self._websocket = None

        self._task.cancel()
        self._task = None

        __log__.info(f'NODE | \'{self.identifier}\' has been disconnected.')

    async def destroy(self, *, force: bool = False) -> None:

        await self.disconnect(force=force)
        del self._client.nodes[self.identifier]

        __log__.info(f'NODE | \'{self.identifier}\' has been destroyed.')

    async def send(self, op, **payload) -> None:

        if not self.is_connected:
            raise NodeConnectionClosed(f'Node \'{self.identifier}\' is not connected.')

        data = {'op': op.value, 'd': data}

        await self._websocket.send_json(data)
        __log__.debug(f'WEBSOCKET | Node \'{self.identifier}\' sent a \'{op}\' payload. | Payload: {data}')

    #

    async def _listen(self) -> None:

        backoff = ExponentialBackoff(base=7)

        while True:

            message = await self._websocket.receive()

            if message.type is aiohttp.WSMsgType.CLOSED:

                self._available = False

                for player in self._players.copy().values():
                    await player.destroy()

                retry = backoff.delay()
                __log__.warning(f'WEBSOCKET | \'{self.identifier}\'s websocket is disconnected, sleeping for {round(retry)} seconds.')
                await asyncio.sleep(retry)

                if not self.is_connected:
                    __log__.warning(f'WEBSOCKET | \'{self.identifier}\'s websocket is disconnected, attempting reconnection.')
                    self.client.bot.loop.create_task(self._reconnect())

            else:

                data = message.json()

                try:
                    op = Op(data.get('op', None))
                except ValueError:
                    __log__.warning(f'WEBSOCKET | \'{self.identifier}\' received payload with invalid/missing op code. | Payload: {data}')
                    continue

                else:
                    __log__.debug(f'WEBSOCKET | \'{self.identifier}\' received payload with op \'{op}\'. | Payload: {data}')
                    await self.client.bot.loop.create_task(self._handle_message(op=op, data=data.get('d')))

    async def _handle_payload(self, op, data: dict[str, Any]) -> None:

        if op is Op.PLAYER_UPDATE:

            if not (player := self.players.get(int(data.get('guild_id')))):
                return

            await player._update_state(data)

        elif op is Op.PLAYER_EVENT:

            if not (player := self.players.get(int(data.get('guild_id')))):
                return

            player._dispatch_event(data)

        elif op is Op.STATS:
            self._stats = ObsidianStats(data)
