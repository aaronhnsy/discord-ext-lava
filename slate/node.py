# Future
from __future__ import annotations

# Standard Library
import asyncio
import contextlib
import json
import logging
from typing import Any, Generic, Literal

# Packages
import aiohttp
import spotipy

# Local
from .exceptions import (
    HTTPError,
    InvalidPassword,
    NodeAlreadyConnected,
    NodeConnectionError,
    NodeNotConnected,
    NoResultsFound,
    SearchFailed,
)
from .objects.collection import Collection
from .objects.enums import Provider, Source
from .objects.search import Search
from .objects.track import Track
from .types import BotT, JSONDumps, JSONLoads, PlayerT
from .utils import (
    LOAD_FAILED,
    MISSING,
    NO_MATCHES,
    OBSIDIAN_TO_LAVALINK_OP_MAP,
    PLAYLIST_LOADED,
    SOURCE_MAP,
    SPOTIFY_URL_REGEX,
    TRACK_LOADED,
    Backoff,
)


__all__ = (
    "Node",
)


LOGGER: logging.Logger = logging.getLogger("slate.node")


class Node(Generic[BotT, PlayerT]):
    """
    A Node handles the interactions between your bot and a provider server such as obsidian or lavalink. These
    interactions include connecting to the websocket, searching for tracks, and managing player state.

    See :meth:`Pool.create_node` for more information about creating a node.
    """

    def __init__(
        self,
        *,
        bot: BotT,
        provider: Provider,
        identifier: str,
        host: str | None = None,
        port: str | None = None,
        ws_url: str | None = None,
        rest_url: str | None = None,
        password: str | None = None,
        resume_key: str | None = None,
        # JSON Callables
        json_dumps: JSONDumps | None = None,
        json_loads: JSONLoads | None = None,
        # Spotify
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> None:

        if (host is None or port is None) and (ws_url is None or rest_url is None):
            raise ValueError("You must set either the host and port or ws_url and rest_url parameters.")

        self._bot: BotT = bot

        self._provider: Provider = provider
        self._identifier: str = identifier
        self._host: str | None = host
        self._port: str | None = port
        self._ws_url: str | None = ws_url
        self._rest_url: str | None = rest_url
        self._password: str | None = password

        self._json_dumps: JSONDumps = json_dumps or json.dumps
        self._json_loads: JSONLoads = json_loads or json.loads

        self._spotify: spotipy.Client | None = spotipy.Client(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
        ) if (spotify_client_id and spotify_client_secret) else None

        self._session: aiohttp.ClientSession = aiohttp.ClientSession()
        self._websocket: aiohttp.ClientWebSocketResponse | None = None
        self._task: asyncio.Task[None] | None = None
        self._backoff: Backoff = MISSING

        self._players: dict[int, PlayerT] = {}

    def __repr__(self) -> str:
        return f"<slate.Node player_count={len(self._players)}>"

    # Properties

    @property
    def bot(self) -> BotT:
        """
        The bot instance that this node is attached to.
        """
        return self._bot

    @property
    def provider(self) -> Provider:
        """
        An enum value indicating which external application this node is attached to.
        """
        return self._provider

    @property
    def identifier(self) -> str:
        """
        A unique identifier for this node.
        """
        return self._identifier

    @property
    def rest_url(self) -> str:
        """
        The url used to make HTTP requests to the provider server.
        """
        return self._rest_url or f"http://{self._host}:{self._port}"

    @property
    def ws_url(self) -> str:
        """
        The url used for WebSocket connections with the provider server.
        """
        return self._ws_url or f"ws://{self._host}:{self._port}{'/magma' if self.provider is Provider.OBSIDIAN else ''}"

    @property
    def players(self) -> dict[int, PlayerT]:
        """
        A mapping of guild id to player instance that this node is managing.
        """
        return self._players

    # Utilities

    def is_listening(self) -> bool:
        return self._task is not None and not self._task.done()

    def is_connected(self) -> bool:
        """
        Returns ``True`` if the node is connected to the provider server, ``False`` otherwise.
        """
        return self._websocket is not None and not self._websocket.closed

    # Connection

    async def connect(self) -> None:
        """
        Connects this node to its provider server.
        """

        if self.is_connected():
            raise NodeAlreadyConnected(f"Node '{self.identifier}' is already connected.")

        # Local
        from . import __version__
        assert self._bot.user is not None

        headers = {
            "Client-Name": f"Slate/{__version__}",
            "User-Id": str(self._bot.user.id),
        }
        if self._password:
            headers["Authorization"] = self._password

        try:
            websocket = await self._session.ws_connect(
                self.ws_url,
                headers=headers
            )

        except Exception as error:

            if isinstance(error, aiohttp.WSServerHandshakeError) and error.status == 401:
                LOGGER.error((message := f"Node '{self.identifier}' failed to connect due to an invalid password."))
                raise InvalidPassword(message)

            LOGGER.error((message := f"Node '{self.identifier}' failed to connect."))
            raise NodeConnectionError(message)

        else:

            self._websocket = websocket
            self._backoff = Backoff(base=3, max_time=60, max_tries=5)

            if not self.is_listening():
                self._task = asyncio.create_task(self._listen())

            self.bot.dispatch("node_connected", self)
            LOGGER.info(f"Node '{self.identifier}' has connected to its websocket.")

    async def disconnect(self) -> None:
        """
        Disconnects this node from its provider server.
        """

        if self.is_listening():
            assert isinstance(self._task, asyncio.Task)
            self._task.cancel()

        self._task = None

        if self.is_connected():
            assert isinstance(self._websocket, aiohttp.ClientWebSocketResponse)
            await self._websocket.close()

        self._websocket = None

        self.bot.dispatch("node_disconnected", self)
        LOGGER.info(f"Node '{self.identifier}' has disconnected from its websocket.")

    # WebSocket

    async def _listen(self) -> None:

        while True:

            assert isinstance(self._websocket, aiohttp.ClientWebSocketResponse)
            message = await self._websocket.receive()

            if message.type is aiohttp.WSMsgType.CLOSED:

                with contextlib.suppress(NodeConnectionError):
                    await self.connect()

                if self.is_connected():
                    continue

                LOGGER.warning(
                    f"Node '{self.identifier}'s websocket was closed, attempting "
                    f"reconnection in {(delay := self._backoff.calculate()):.2f} seconds."
                )
                await asyncio.sleep(delay)

            else:
                payload = message.json(loads=self._json_loads)
                asyncio.create_task(
                    self._receive_payload(
                        payload["op"],
                        data=payload["d"] if "d" in payload else payload
                    )
                )

    async def _receive_payload(
        self,
        op: str | int,
        /, *,
        data: dict[str, Any]
    ) -> None:

        LOGGER.debug(f"Node '{self.identifier}' received a payload with op '{op}'.\nData: {data}")

        if op in (1, "stats"):
            self._stats = None  # Stats(data)
            return

        player = self._players.get(int(data["guild_id"] if self.provider is Provider.OBSIDIAN else data["guildId"]))

        if op in (4, "event"):

            if not player:
                LOGGER.warning(f"Node '{self.identifier}' received a player event for a guild without a player.\nData: {data}")
            else:
                player._dispatch_event(data)
            return

        if op in (5, "playerUpdate"):

            if not player:
                LOGGER.warning(f"Node '{self.identifier}' received a player update for a guild without a player.\nData: {data}")
            else:
                player._update_state(data)
            return

        LOGGER.warning(f"Node '{self.identifier}' received a payload with an unknown op '{op}'.\nData: {data}")

    async def _send_payload(
        self,
        op: int,
        /, *,
        data: Any | None = None,
        guild_id: str | None = None
    ) -> None:

        if not self.is_connected():
            raise NodeNotConnected(f"Node '{self.identifier}' is not connected.")

        assert isinstance(self._websocket, aiohttp.ClientWebSocketResponse)

        if not data:
            data = {}

        if self.provider is Provider.OBSIDIAN:
            if guild_id:
                data["guild_id"] = guild_id
            data = {
                "op": op,
                "d":  data
            }
        else:
            if guild_id:
                data["guildId"] = guild_id
            data = {
                "op": OBSIDIAN_TO_LAVALINK_OP_MAP[op],
                **data
            }

        _json = self._json_dumps(data)
        if isinstance(_json, bytes):
            _json = _json.decode("utf-8")

        await self._websocket.send_str(_json)
        LOGGER.debug(f"Node '{self.identifier}' sent a payload with op '{op}'.\nData: {data}")

    # REST

    async def _request(
        self,
        method: Literal["GET"],
        /, *,
        path: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        url = f"{self.rest_url}{path}"
        headers = {
            "Authorization": self._password,
            "Client-Name":   "Slate"
        }

        response: aiohttp.ClientResponse = MISSING

        for tries in range(5):

            try:
                async with self._session.request(
                        method,
                        url=url,
                        headers=headers,
                        params=parameters,
                ) as response:

                    if 200 <= response.status < 300:
                        LOGGER.info(f"'{method}' @ '{response.url}' -> '{response.status}'")
                        return await response.json(loads=self._json_loads)

            except OSError as error:
                if tries >= 4 or error.errno not in (54, 10054):
                    raise

            delay = 1 + tries * 2

            LOGGER.warning(f"'{method}' @ '{response.url}' -> '{response.status}', retrying in {delay}s.")
            await asyncio.sleep(delay)

        message = f"'{method}' @ '{response.url}' -> '{response.status}', all five retries used."

        LOGGER.error(message)
        raise HTTPError(response, message=message)

    async def _spotify_search(
        self,
        *,
        _id: str,
        _type: str,
        extras: dict[str, Any] | None = None
    ) -> Search:

        assert self._spotify is not None

        try:
            if _type == "album":
                result = await self._spotify.get_full_album(_id)
                tracks = [Track._from_spotify_track(track, result, extras) for track in result.tracks]

            elif _type == "playlist":
                result = await self._spotify.get_full_playlist(_id)
                tracks = [Track._from_spotify_track(track, result, extras) for track in result.tracks]

            elif _type == "artist":
                result = await self._spotify.get_artist(_id)
                tracks = [
                    Track._from_spotify_track(track, result, extras)
                    for track in await self._spotify.get_artist_top_tracks(_id)
                ]

            else:  # _type == "track":
                result = await self._spotify.get_track(_id)
                tracks = [Track._from_spotify_track(result, result, extras)]

        except spotipy.NotFound:
            raise NoResultsFound(search=_id, source=Source.SPOTIFY, type=_type)
        except spotipy.HTTPError:
            raise SearchFailed(data={"message": "Error while accessing spotify API.", "severity": "COMMON"})

        return Search(
            source=Source.SPOTIFY,
            type=_type,
            result=result,
            tracks=tracks
        )

    async def _source_search(
        self,
        *,
        search: str,
        source: Source,
        extras: dict[str, Any] | None = None
    ) -> Search:

        data = await self._request(
            "GET",
            path="/loadtracks",
            parameters={
                "identifier": f"{SOURCE_MAP.get(source, '')}{search}"
            }
        )
        load_type = data.get("load_type", data.get("loadType"))

        if load_type in NO_MATCHES:
            raise NoResultsFound(search=search, source=source, type="track")
        elif load_type in LOAD_FAILED:
            raise SearchFailed(data["exception"])

        elif load_type in TRACK_LOADED:

            tracks = [
                Track(id=track["track"], info=track["info"], extras=extras)
                for track in data["tracks"]
            ]
            return Search(
                source=tracks[0].source,
                type="track",
                result=tracks,
                tracks=tracks
            )

        elif load_type in PLAYLIST_LOADED:

            if self.provider is Provider.OBSIDIAN:
                info = data["collection_info"]
            else:
                info = data["playlistInfo"]
                info["url"] = search

            collection = Collection(info=info, tracks=data["tracks"], extras=extras)

            return Search(
                source=collection.source,
                type="collection",
                result=collection,
                tracks=collection.tracks
            )

        else:
            raise SearchFailed(data={"message": "Unknown '/loadtracks' load type.", "severity": "FAULT"})

    async def search(
        self,
        search: str,
        /, *,
        source: Source = Source.NONE,
        **extras: Any
    ) -> Search:
        """
        Requests search results from this node's provider server, or other services like spotify.

        Parameters
        ----------
        search: :class:`str`
            The search query.
        source: :class:`~slate.Source`
            The source to request results from. Defaults to :attr:`Source.NONE`.

        Raises
        ------
        :exc:`~slate.NoResultsFound`
            If no results were found.
        :exc:`~slate.SearchFailed`
            If the search failed.
        :exc:`~slate.HTTPError`
            If the HTTP request failed.

        Returns
        -------
        :class:`~slate.Search`
        """

        if self._spotify and (match := SPOTIFY_URL_REGEX.match(search)):
            return await self._spotify_search(_id=match.group("id"), _type=match.group("type"), extras=extras)

        return await self._source_search(search=search, source=source, extras=extras)
