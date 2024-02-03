import asyncio
import itertools
import json as _json
import logging
import random
import string
import traceback
from typing import TYPE_CHECKING, Any, Generic, cast
from typing_extensions import TypeVar

import aiohttp
import spotipy

from ._backoff import Backoff
from ._utilities import SPOTIFY_REGEX, DeferredMessage, chunks, json_or_text, ordinal
from .exceptions import LinkAlreadyConnected, LinkConnectionError, NoSearchResults, SearchError, SearchFailed
from .objects.playlist import Playlist
from .objects.result import Result
from .objects.stats import Stats
from .objects.track import Track
from .types.common import JSON, JSONDumps, JSONLoads, SpotifySearchType
from .types.rest import RequestData, RequestKwargs, RequestMethod, RequestParameters, SearchData
from .types.websocket import Payload


if TYPE_CHECKING:
    from .player import Player  # type: ignore


__all__ = ["Link"]

__ws_log__: logging.Logger = logging.getLogger("lava.websocket")
__rest_log__: logging.Logger = logging.getLogger("lava.rest")

PlayerT = TypeVar("PlayerT", bound="Player", default="Player", covariant=True)


class Link(Generic[PlayerT]):

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

        self._spotify: spotipy.Client | None = spotipy.Client(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
        ) if spotify_client_id and spotify_client_secret else None

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
        return "<discord.ext.lava.Link>"

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
            raise LinkAlreadyConnected(f"Link '{self.identifier}' is already connected.")
        try:
            from . import __version__
            if self._session is None:
                self._session = aiohttp.ClientSession()
            websocket = await self._session.ws_connect(
                url=f"{self._ws_url or f'ws://{self._host}:{self._port}'}/v4/websocket",
                headers={
                    "Authorization": self._password,
                    "User-Id":       str(self._user_id),
                    "Client-Name":   f"discord-ext-lava/{__version__}"
                }
            )
        except Exception as error:
            if isinstance(error, aiohttp.WSServerHandshakeError):
                if error.status == 401:
                    message = f"Link '{self.identifier}' could not connect to its websocket due to an incorrect " \
                              f"password. "
                elif error.status in {403, 404}:
                    message = f"Link '{self.identifier}' could not connect to its websocket, if you're using the " \
                              f"`ws_url` parameter please make sure its path is correct."
                else:
                    message = f"Link '{self.identifier}' could not connect to its websocket, encountered a " \
                              f"'{error.status}' status code error."
            else:
                message = f"Link '{self.identifier}' raised '{error.__class__.__name__}' while connecting to its " \
                          f"websocket."
            __ws_log__.error(message)
            raise LinkConnectionError(message)

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

    async def _process_payload(self, payload: Payload, /) -> None:
        __ws_log__.debug(
            f"Link '{self.identifier}' received a '{payload['op']}' payload.\n%s",
            DeferredMessage(_json.dumps, payload, indent=4),
        )
        match payload["op"]:
            case "ready":
                self._session_id = payload["sessionId"]
                self._ready_event.set()
                __ws_log__.info(f"Link '{self.identifier}' is ready.")
            case "stats":
                self._stats = Stats(payload)
            case "event":
                if not (player := self._players.get(int(payload["guildId"]))):
                    __ws_log__.warning(
                        f"Link '{self.identifier}' received a '{payload['type']}' event for a non-existent player "
                        f"with id '{payload['guildId']}'."
                    )
                    return
                player._handle_event(payload)
            case "playerUpdate":
                if not (player := self._players.get(int(payload["guildId"]))):
                    __ws_log__.warning(
                        f"Link '{self.identifier}' received a player update for a non-existent player "
                        f"with id '{payload['guildId']}'."
                    )
                    return
                player._handle_player_update(payload["state"])
            case _:  # pyright: ignore - lavalink could add new op codes.
                __ws_log__.error(
                    f"Link '{self.identifier}' received a payload with an unhandled op code: '{payload["op"]}'."
                )

    async def _listen(self) -> None:
        while True:
            if self._websocket is None:
                await self._reset_state()
                break
            message = await self._websocket.receive()
            if message.type is aiohttp.WSMsgType.CLOSED:
                # Log a warning for the first reconnect attempt.
                if self._backoff.tries == 0:
                    __ws_log__.warning(
                        f"Link '{self.identifier}' was unexpectedly disconnected from its websocket. It will now "
                        f"attempt to reconnect up to {self._backoff.max_tries} times with a backoff delay."
                    )
                # Calculate the backoff delay and sleep.
                __ws_log__.warning(
                    f"Link '{self.identifier}' is attempting its {ordinal(self._backoff.tries + 1)} reconnection "
                    f"in {(delay := self._backoff.calculate()):.2f} seconds."
                )
                await asyncio.sleep(delay)

                try:
                    # Attempt to reconnect to the websocket.
                    await self.connect()
                except LinkConnectionError as error:
                    # Print the error manually because we don't want an error to be raised inside the task.
                    traceback.print_exception(type(error), error, error.__traceback__)
                    # Cancel the task (and reset other vars) to stop further reconnection attempts.
                    if self._backoff.max_tries and self._backoff.tries == self._backoff.max_tries:
                        __ws_log__.warning(
                            f"Link '{self.identifier}' has attempted to reconnect {self._backoff.max_tries} times "
                            f"with no success. It will not attempt to reconnect again."
                        )
                        await self._reset_state()
                        break
                    # Continue to the next reconnection attempt.
                    continue
                else:
                    # If no error was raised, continue the outer loop as we should've reconnected.
                    __ws_log__.info(f"Link '{self.identifier}' was able to reconnect to its websocket.")
                    continue

            asyncio.create_task(
                self._process_payload(
                    cast(Payload, self._json_loads(message.data))
                )
            )

    # rest

    async def _request(
        self,
        method: RequestMethod,
        path: str,
        /, *,
        parameters: RequestParameters | None = None,
        data: RequestData | None = None,
    ) -> Any:
        if self._session is None:
            self._session = aiohttp.ClientSession()

        url = f"{(self._rest_url or f'http://{self._host}:{self._port}/').removesuffix('/')}{path}"

        kwargs: RequestKwargs = {"headers": {"Authorization": self._password}}
        if parameters is not None:
            kwargs["params"] = parameters
        if data is not None:
            kwargs["headers"]["Content-Type"] = "application/json"
            kwargs["data"] = self._json_dumps(cast(JSON, data))

        async with self._session.request(method, url, **kwargs) as response:
            response_data = await json_or_text(response, json_loads=self._json_loads)
            __rest_log__.debug(
                f"{method} -> '{url}' -> {response.status}.\n"
                f"Request Parameters:{"\n" if parameters else " "}%s\n"
                f"Request Data:{"\n" if data else " "}%s\n"
                f"Response Data:{"\n" if response_data else " "}%s",
                DeferredMessage(_json.dumps, parameters or {}, indent=4),
                DeferredMessage(_json.dumps, data or {}, indent=4),
                DeferredMessage(_json.dumps, response_data or {}, indent=4),
            )
            if 200 <= response.status < 300:
                return response_data

    async def _spotify_search(self, _type: SpotifySearchType, _id: str, /) -> Result:
        try:
            assert self._spotify is not None
            match _type:
                case "album":
                    source = await self._spotify.get_full_album(_id)
                    tracks = [
                        Track._from_spotify_track(track) for track in
                        itertools.chain.from_iterable(
                            [
                                filter(
                                    None,
                                    (await self._spotify.get_tracks([track.id for track in chunk])).values()
                                )
                                for chunk in chunks(source.tracks, 50)
                            ]
                        )
                    ]
                case "playlist":
                    source = await self._spotify.get_full_playlist(_id)
                    tracks = [Track._from_spotify_track(track) for track in source.tracks]
                case "artist":
                    source = await self._spotify.get_artist(_id)
                    tracks = [
                        Track._from_spotify_track(track) for track in
                        await self._spotify.get_artist_top_tracks(_id)
                    ]
                case "track":
                    source = await self._spotify.get_track(_id)
                    tracks = [Track._from_spotify_track(source)]
        except spotipy.NotFound:
            raise NoSearchResults(search=_id)
        except spotipy.HTTPError as error:
            raise SearchFailed(
                {
                    "message":  "Error while accessing the Spotify API.",
                    "severity": "suspicious",
                    "cause":    error.message
                }
            )
        # noinspection PyUnboundLocalVariable
        return Result(source=source, tracks=tracks)

    async def _lavalink_search(self, search: str, /) -> Result:
        data: SearchData = cast(
            SearchData,
            await self._request("GET", "/v4/loadtracks", parameters={"identifier": search})
        )
        match data["loadType"]:
            case "track":
                source = Track(data["data"])
                tracks = [source]
            case "playlist":
                source = Playlist(data["data"])
                tracks = source.tracks
            case "search":
                source = [Track(track) for track in data["data"]]
                tracks = source
            case "empty":
                raise NoSearchResults(search=search)
            case "error":
                raise SearchFailed(data["data"])
            case _:  # pyright: ignore - lavalink could add new load types
                msg = f"Unknown load type: '{data["load_type"]}'. Please report this to the library author."
                __rest_log__.error(msg)
                raise SearchError(msg)
        return Result(source=source, tracks=tracks)

    async def search(self, search: str, /) -> Result:
        if (match := SPOTIFY_REGEX.match(search)) is not None and self._spotify is not None:
            return await self._spotify_search(match["type"], match["id"])  # pyright: ignore
        else:
            return await self._lavalink_search(search)
