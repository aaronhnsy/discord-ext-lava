from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import random
import string
from collections.abc import Callable
from typing import Any, Generic

import aiohttp
import discord
import spotipy
from discord.ext import commands
from typing_extensions import TypeVar

from .backoff import Backoff
from .exceptions import AlreadyConnected, IncorrectPassword, NodeConnectionError
from .types.payloads import Payload


__all__ = (
    "Node",
)

BotT = TypeVar("BotT", bound=commands.Bot | commands.AutoShardedBot, default=commands.Bot)
PlayerT = TypeVar("PlayerT", bound=Any, default=Any)

LOGGER: logging.Logger = logging.getLogger("discord.ext.lava.node")

ordinal: Callable[[int], str] = lambda n: "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


class Node(Generic[BotT, PlayerT]):

    def __init__(
        self,
        *,
        bot: BotT,
        password: str,
        host: str | None = None,
        port: str | None = None,
        ws_url: str | None = None,
        rest_url: str | None = None,
        json_dumps: Callable[..., str] | None = None,
        json_loads: Callable[..., dict[str, Any]] | None = None,
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:

        if (host is None and port is None) and (ws_url is None and rest_url is None):
            raise ValueError("You must provide either the `host` and `port` OR `ws_url` and `rest_url` parameters.")

        self._bot = bot
        self._password = password

        self._host = host
        self._port = port
        self._ws_url = ws_url
        self._rest_url = rest_url

        self._json_dumps = json_dumps or json.dumps
        self._json_loads = json_loads or json.loads

        if spotify_client_id is not None and spotify_client_secret is not None:
            self._spotify = spotipy.Client(
                client_id=spotify_client_id,
                client_secret=spotify_client_secret,
            )
        else:
            self._spotify = None

        self._session = session

        self._backup_identifier: str = "".join(random.sample(string.ascii_letters, 20))
        self._identifier: str | None = None

        self._backoff: Backoff = discord.utils.MISSING
        self._websocket: aiohttp.ClientWebSocketResponse | None = None
        self._task: asyncio.Task[None] | None = None

    # properties

    @property
    def identifier(self) -> str:
        return self._identifier or self._backup_identifier

    # utility methods

    def is_connected(self) -> bool:
        return self._websocket is not None and self._websocket.closed is False

    # connection management

    async def connect(self) -> None:

        if self.is_connected():
            raise AlreadyConnected(f"Node '{self.identifier}' is already connected.")

        from . import __version__
        assert self._bot.user is not None

        if not self._session:
            self._session = aiohttp.ClientSession()

        url = self._ws_url or f"ws://{self._host}:{self._port}/v3/websocket"
        headers = {
            "Authorization": self._password,
            "User-Id":       str(self._bot.user.id),
            "Client-Name":   f"discord-ext-lava/{__version__}"
        }

        try:
            websocket = await self._session.ws_connect(url, headers=headers)
        except Exception as error:
            if isinstance(error, aiohttp.WSServerHandshakeError) and error.status == 401:
                LOGGER.error(message := f"Incorrect password for '{url}'.")
                raise IncorrectPassword(message)
            else:
                LOGGER.error(message := f"Error while connecting to '{url}'.")
                raise NodeConnectionError(message)

        self._backoff = Backoff(base=2, max_time=60 * 5, max_tries=5)
        self._websocket = websocket

        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._listen())

    async def _clear_state(self) -> None:

        if self._task is not None and self._task.done() is False:
            self._task.cancel()

        self._task = None

        if self._websocket is not None and self._websocket.closed is False:
            await self._websocket.close()

        self._websocket = None

    async def _listen(self) -> None:

        while True:

            assert isinstance(self._websocket, aiohttp.ClientWebSocketResponse)
            message = await self._websocket.receive()

            if message.type is aiohttp.WSMsgType.CLOSED:

                if self.is_connected():
                    continue

                # Log a warning for the first reconnection attempt.
                if self._backoff.tries == 0:
                    LOGGER.warning(
                        f"Node '{self.identifier}' was unexpectedly disconnected from its websocket and is now "
                        f"entering a reconnection backoff period."
                    )

                # Sleep for a backoff period.
                LOGGER.warning(
                    f"Node '{self.identifier}' attempting {ordinal(self._backoff.tries + 1)} reconnection attempt "
                    f"in {(delay := self._backoff.calculate()):.2f} seconds."
                )
                await asyncio.sleep(delay)

                # Attempt to reconnect to the websocket.
                with contextlib.suppress(NodeConnectionError):
                    await self.connect()

                # Stop backoff period if we've reached the max amount of retries.
                if self._backoff.max_tries and self._backoff.tries == self._backoff.max_tries:
                    LOGGER.warning(
                        f"Node '{self.identifier}' has reached the maximum amount of reconnection attempts and will "
                        f"not attempt to reconnect again."
                    )
                    await self._clear_state()
                    break

            asyncio.create_task(self._process_payload(self._json_loads(message.data)))  # type: ignore

    async def _process_payload(self, payload: Payload) -> None:

        if payload["op"] == "ready":
            raise NotImplementedError
        elif payload["op"] == "playerUpdate":
            raise NotImplementedError
        elif payload["op"] == "stats":
            raise NotImplementedError
        elif payload["op"] == "event":
            raise NotImplementedError
