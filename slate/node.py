# Future
from __future__ import annotations

# Standard Library
import abc
import asyncio
import json
import logging
from typing import Any, Callable, Generic, Literal, TypeVar, Union

# Packages
import aiohttp
import aiospotify
import discord
from discord.ext import commands

# My stuff
from slate import exceptions


__all__ = (
    "BaseNode",
)
__log__: logging.Logger = logging.getLogger("slate.node")


BotT = TypeVar("BotT", bound=Union[discord.Client, discord.AutoShardedClient, commands.Bot, commands.AutoShardedBot])


class BaseNode(abc.ABC, Generic[BotT]):

    def __init__(
        self,
        bot: BotT,
        identifier: str,
        host: str,
        port: str,
        password: str,
        session: aiohttp.ClientSession | None = None,
        json_dumps: Callable[..., str] | None = None,
        json_loads: Callable[..., dict[str, Any]] | None = None,
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> None:

        self._bot: BotT = bot
        self._identifier: str = identifier

        self._host: str = host
        self._port: str = port
        self._password: str = password

        self._session: aiohttp.ClientSession = session or aiohttp.ClientSession()

        self._json_dumps: Callable[..., str] = json_dumps or json.dumps
        self._json_loads: Callable[..., dict[str, Any]] = json_loads or json.loads

        self._spotify: aiospotify.Client | None = None
        if spotify_client_id and spotify_client_secret:
            self._spotify = aiospotify.Client(client_id=spotify_client_id, client_secret=spotify_client_secret, session=self._session)

        self._websocket: aiohttp.ClientWebSocketResponse | None = None
        self._task: asyncio.Task | None = None

    #

    async def request(
        self,
        method: Literal["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        /,
        *,
        endpoint: str,
        parameters: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        url = f"{self._http_url}{endpoint}"
        headers = {
            "Authorization": self._password,
            "Client-Name":   "Slate"
        }

        for tries in range(5):

            try:

                async with self._session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=parameters,
                        data=data
                ) as response:

                    if 200 <= response.status < 300:

                        response_data = await response.json(loads=self._json_loads)

                        __log__.debug(f"'{method}' @ '{response.url}' success.\nPayload: {response_data}")
                        return response_data

                    delay = 1 + tries * 2

                    __log__.debug(f"'{method}' @ '{response.url}' received '{response.status}' status code, retrying in {delay}s.")
                    await asyncio.sleep(delay)

            except OSError as error:
                if tries < 4 and error.errno in (54, 10054):

                    delay = 1 + tries * 2

                    __log__.debug(f"'{method}' @ '{response.url}' raised OSError, retrying in {delay}s.")
                    await asyncio.sleep(delay)

                    continue
                raise

        if response:
            __log__.debug(f"'{method}' @ '{response.url}' received '{response.status}' status code, all 5 retries used.")
            raise exceptions.HTTPError(response, message=f"A {response.status} status code was received, 5 retries used.")

        raise RuntimeError("This shouldn't happen.")

    def is_connected(self) -> bool:
        return self._websocket is not None and self._websocket.closed is False

    #

    @property
    @abc.abstractmethod
    def _http_url(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _ws_url(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def players(self) -> Any:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def stats(self) -> Any:
        raise NotImplementedError

    #

    @abc.abstractmethod
    async def connect(
        self,
        *,
        raise_on_fail: bool = True
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def disconnect(
        self,
        *,
        force: bool = False
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def destroy(
        self,
        *,
        force: bool = False
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def _listen(
        self
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def _handle_payload(
        self,
        payload: dict[str, Any],
        /
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def _send_payload(
        self,
        op: Any,
        /,
        *,
        payload: dict[str, Any]
    ) -> None:
        raise NotImplementedError
