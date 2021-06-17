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
import json
import logging
from typing import Any, Callable, Generic, Literal, Optional, TypeVar, Union

from aiohttp import ClientSession, ClientWebSocketResponse
from discord import Client, VoiceRegion
from discord.ext.commands import AutoShardedBot, Bot
from spotify import Client as SpotifyClient, HTTPClient as SpotifyHTTPClient

from .exceptions import HTTPError, NodeNotConnected
from .utils.backoff import ExponentialBackoff


__all__ = ['BaseNode']
__log__: logging.Logger = logging.getLogger('slate.node')


BotT = TypeVar('BotT', bound=Union[Client, Bot, AutoShardedBot])


def ordinal(number: int) -> str:
    return f"{number}{'tsnrhtdd'[(number // 10 % 10 != 1) * (number % 10 < 4) * number % 10::4]}"


class BaseNode(abc.ABC, Generic[BotT]):

    def __init__(self, bot: BotT, host: str, port: str, password: str, identifier: str, region: Optional[VoiceRegion] = None, **kwargs) -> None:

        self._bot: BotT = bot
        self._host: str = host
        self._port: str = port
        self._password: str = password
        self._identifier: str = identifier
        self._region: Optional[VoiceRegion] = region

        self._dumps: Callable[[dict[str, Any]], str] = kwargs.get('dumps') or json.dumps
        self._loads: Callable[[str], dict[str, Any]] = kwargs.get('loads') or json.loads

        self._spotify_client_id: Optional[str] = kwargs.get('spotify_client_id')
        self._spotify_client_secret: Optional[str] = kwargs.get('spotify_client_secret')

        self._spotify: Optional[SpotifyClient] = None
        self._spotify_http: Optional[SpotifyHTTPClient] = None

        if self._spotify_client_id and self._spotify_client_secret:
            self._spotify = SpotifyClient(self._spotify_client_id, self._spotify_client_secret)
            self._spotify_http = SpotifyHTTPClient(self._spotify_client_id, self._spotify_client_secret)

        self._session: ClientSession = kwargs.get('session') or ClientSession()

        self._websocket: Optional[ClientWebSocketResponse] = None
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
    def region(self) -> Optional[VoiceRegion]:
        return self._region

    #

    @property
    def spotify(self) -> Optional[SpotifyClient]:
        return self._spotify

    @property
    def spotify_http(self) -> Optional[SpotifyHTTPClient]:
        return self._spotify_http

    #

    @property
    def session(self) -> ClientSession:
        return self._session

    @property
    def websocket(self) -> Optional[ClientWebSocketResponse]:
        return self._websocket

    #

    def is_connected(self) -> bool:
        return self._websocket is not None and not self._websocket.closed

    #

    @property
    @abc.abstractmethod
    def players(self) -> Any:
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

    async def send(self, op: Any, **data) -> None:

        if not self.is_connected():
            raise NodeNotConnected(f'Node \'{self.identifier}\' is not connected.')

        payload = {'op': op.value, 'd': data}

        data = self._dumps(payload)
        if isinstance(data, bytes):
            data = data.decode('utf-8')

        await self._websocket.send_str(data)

        __log__.debug(f'NODE | \'{self.identifier}\' node sent a {op!r} payload. | Payload: {payload}')

    #

    async def _request(self, method: Literal['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'], endpoint: str, **parameters: Any) -> dict[str, Any]:

        backoff = ExponentialBackoff()
        url = f'{self.http_url}{endpoint}'
        headers = {'Authorization': self._password, 'Client-Name': f'Slate/2021.05.26'}

        for _ in range(3):

            async with self._session.request(method=method, url=url, headers=headers, params=parameters) as response:

                if 200 <= response.status < 300:
                    return await response.json(loads=self._loads)

                delay = backoff.delay()
                __log__.warning(f'NODE | \'{response.status}\' status code while requesting from \'{response.url}\', retrying in {round(delay)}s. ({ordinal(_ + 1)} retry)')

                await asyncio.sleep(delay)

        __log__.error(f'NODE | \'{response.status}\' status code while requesting from \'{response.url}\', 3 retries used.')
        raise HTTPError(f'\'{response.status}\' status code while requesting from \'{response.url}\', 3 retries used.', response=response)

    #

    @abc.abstractmethod
    async def _listen(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def _handle_payload(self, op: Any, data: dict[str, Any]) -> None:
        raise NotImplementedError
