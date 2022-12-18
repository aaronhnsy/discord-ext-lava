from __future__ import annotations

import asyncio
import json as _json
import logging
import random
import string
import traceback
from typing import Generic, TYPE_CHECKING

import aiohttp
import discord.utils
import spotipy
from typing_extensions import TypeVar

from ._backoff import Backoff
from ._utilities import ordinal
from .exceptions import NodeAlreadyConnected, NodeConnectionError
from .objects.stats import Stats
from .types.common import JSON, JSONDumps, JSONLoads
from .types.payloads import Payload
from .types.rest import HTTPMethod


if TYPE_CHECKING:
    from .player import Player  # type: ignore


__all__: list[str] = ["Node"]
__log__: logging.Logger = logging.getLogger("discord-ext-lava.node")

PlayerT = TypeVar("PlayerT", bound="Player", default="Player")


class Node(Generic[PlayerT]):

    def __init__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        ws_url: str | None = None,
        rest_url: str | None = None,
        password: str,
        user_id: int,
        json_dumps: JSONDumps | None = None,
        json_loads: JSONLoads | None = None,
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> None:

        if (host is None or port is None) and (ws_url is None or rest_url is None):
            raise ValueError(
                "You must provide either the `host` and `port` OR `ws_url` and `rest_url` parameters. "
                "`ws_url` and `rest_url` will take precedence over `host` and `port` if both sets are provided."
            )

        self._host: str | None = host
        self._port: int | None = port
        self._ws_url: str | None = ws_url
        self._rest_url: str | None = rest_url

        self._password: str = password
        self._user_id: int = user_id

        self._json_dumps: JSONDumps = json_dumps or _json.dumps
        self._json_loads: JSONLoads = json_loads or _json.loads

        if spotify_client_id is not None and spotify_client_secret is not None:
            self._spotify: spotipy.Client | None = spotipy.Client(
                client_id=spotify_client_id,
                client_secret=spotify_client_secret,
            )
        else:
            self._spotify: spotipy.Client | None = None

        self._backoff: Backoff = Backoff(base=2, max_time=60 * 5, max_tries=5)

        self._task: asyncio.Task[None] | None = None
        self._session: aiohttp.ClientSession | None = None
        self._websocket: aiohttp.ClientWebSocketResponse | None = None

        self._ready_event: asyncio.Event = asyncio.Event()

        self._identifier: str = "".join(random.sample(string.ascii_uppercase, 20))
        self._session_id: str | None = None
        self._stats: Stats | None = None
        self._players: dict[int, PlayerT] = {}

    def __repr__(self) -> str:
        return "<discord.ext.lava.Node>"

    # properties

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def stats(self) -> Stats | None:
        return self._stats

    @property
    def players(self) -> dict[int, PlayerT]:
        return self._players

    # utility methods

    def is_connected(self) -> bool:
        return self._websocket is not None and self._websocket.closed is False

    def is_ready(self) -> bool:
        return self.is_connected() is True and self.session_id is not None

    # websocket

    async def connect(self) -> None:

        if self.is_connected():
            raise NodeAlreadyConnected(f"Node '{self.identifier}' is already connected.")

        if self._session is None:
            self._session = aiohttp.ClientSession()

        try:
            from . import __version__
            websocket = await self._session.ws_connect(
                f"{self._ws_url or f'ws://{self._host}:{self._port}'}/v3/websocket",
                headers={
                    "Authorization": self._password,
                    "User-Id":       str(self._user_id),
                    "Client-Name":   f"discord-ext-lava/{__version__}"
                }
            )

        except Exception as error:
            if isinstance(error, aiohttp.WSServerHandshakeError):
                if error.status == 401:
                    message = f"Node '{self.identifier}' could not connect to its websocket due to an incorrect " \
                              f"password. "
                elif error.status in {403, 404}:
                    message = f"Node '{self.identifier}' could not connect to its websocket, if you're using the " \
                              f"`ws_url` parameter please make sure its path is correct."
                else:
                    message = f"Node '{self.identifier}' could not connect to its websocket, encountered a " \
                              f"'{error.status}' status code error."
            else:
                message = f"Node '{self.identifier}' raised '{error.__class__.__name__}' while connecting to its " \
                          f"websocket."
            __log__.error(message)
            raise NodeConnectionError(message)

        self._backoff.reset()
        self._websocket = websocket

        if self._task is None or self._task.done() is True:
            self._task = asyncio.create_task(self._listen())

    async def _reset_state(self) -> None:

        self._backoff.reset()

        if self._task is not None and self._task.done() is False:
            self._task.cancel()
        self._task = None

        if self._websocket is not None and self._websocket.closed is False:
            await self._websocket.close()
        self._websocket = None

        if self._session is not None:
            await self._session.close()
        self._session = None

    async def _process_payload(self, payload: Payload) -> None:

        __log__.debug(f"Node '{self.identifier}' received a '{payload['op']}' payload.\n{_json.dumps(payload, indent=4)}")

        if payload["op"] == "ready":
            self._session_id = payload["sessionId"]
            self._ready_event.set()
            __log__.info(f"Node '{self.identifier}' is ready.")
            return

        elif payload["op"] == "playerUpdate":
            if not (player := self._players.get(int(payload["guildId"]))):
                __log__.warning(f"Node '{self.identifier}' received a player update for non-existent player with id '{payload['guildId']}'.")
                return
            await player._handle_player_update(payload)

        elif payload["op"] == "stats":
            self._stats = Stats(payload)
            return

        elif payload["op"] == "event":
            if not (player := self._players.get(int(payload["guildId"]))):
                __log__.warning(f"Node '{self.identifier}' received a '{payload['type']}' event for non-existent player with id '{payload['guildId']}'.")
                return
            await player._handle_event(payload)

    async def _listen(self) -> None:

        while True:

            assert isinstance(self._websocket, aiohttp.ClientWebSocketResponse)
            message = await self._websocket.receive()

            if message.type is aiohttp.WSMsgType.CLOSED:

                # Log a warning for the first reconnect attempt.
                if self._backoff.tries == 0:
                    __log__.warning(
                        f"Node '{self.identifier}' was unexpectedly disconnected from its websocket. It will now "
                        f"attempt to reconnect up to {self._backoff.max_tries} times with a backoff delay."
                    )

                # Calculate the backoff delay and sleep.
                __log__.warning(
                    f"Node '{self.identifier}' is attempting its {ordinal(self._backoff.tries + 1)} reconnection "
                    f"in {(delay := self._backoff.calculate()):.2f} seconds."
                )
                await asyncio.sleep(delay)

                try:
                    # Attempt to reconnect to the websocket.
                    await self.connect()

                except NodeConnectionError as error:
                    # Print the error manually because we don't want an error to be raised inside the task.
                    traceback.print_exception(type(error), error, error.__traceback__)

                    # Cancel the task (and reset other vars) to stop further reconnection attempts.
                    if self._backoff.max_tries and self._backoff.tries == self._backoff.max_tries:
                        __log__.warning(
                            f"Node '{self.identifier}' has attempted to reconnect {self._backoff.max_tries} times "
                            f"with no success. It will not attempt to reconnect again."
                        )
                        await self._reset_state()
                        break

                    # Continue to the next reconnection attempt.
                    continue

                else:
                    # If no error was raised, continue the outer loop as we should've reconnected.
                    __log__.info(f"Node '{self.identifier}' was able to reconnect to its websocket.")
                    continue

            asyncio.create_task(
                self._process_payload(self._json_loads(message.data))  # type: ignore
            )

    # rest api

    async def _request(
        self,
        method: HTTPMethod,
        path: str,
        /, *,
        data: JSON | None = None
    ) -> JSON:

        if self._session is None:
            self._session = aiohttp.ClientSession()

        url = f"{self._rest_url or f'http://{self._host}:{self._port}'}/v3{path}"
        headers = {
            "Authorization": self._password,
            "Content-Type":  "application/json"
        }
        json_data = self._json_dumps(data)

        response: aiohttp.ClientResponse = discord.utils.MISSING

        for tries in range(5):
            try:
                async with self._session.request(method=method, url=url, headers=headers, data=json_data) as response:
                    __log__.debug(f"{method} @ '{response.url}' -> {response.status}.\n{_json.dumps(data, indent=4)}")
                    if 200 <= response.status < 300:
                        return await response.json(loads=self._json_loads)

            except OSError as error:
                if tries >= 4 or error.errno not in (54, 10054):
                    raise

            __log__.warning(f"{method} @ '{response.url}' -> {response.status}, retrying in {(delay := 1 + tries * 2)}s.")
            await asyncio.sleep(delay)

        message = f"{method} @ '{response.url}' -> {response.status}, all five retries used."
        __log__.error(message)
        # raise HTTPError(response, message=message)
