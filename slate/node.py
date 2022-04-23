# Future
from __future__ import annotations

# Standard Library
import asyncio
import json
import logging
from typing import Any, Generic, Literal

# Packages
import aiohttp
import spotipy

# Local
from .exceptions import (
    HTTPError,
    NodeConnectionError,
    NodeInvalidPassword,
    NodeNotConnected,
    NoResultsFound,
    SearchFailed,
)
from .objects.collection import Collection
from .objects.enums import Provider, Source
from .objects.search import Search
from .objects.stats import Stats
from .objects.track import Track
from .types import BotT, ContextT, JSONDumps, JSONLoads, PlayerT
from .utils import OBSIDIAN_TO_LAVALINK_OP_MAP, SPOTIFY_URL_REGEX, Backoff


__all__ = (
    "Node",
)
__log__: logging.Logger = logging.getLogger("slate.node")


class Node(Generic[BotT, ContextT, PlayerT]):

    def __init__(
        self,
        provider: Provider,
        bot: BotT,
        identifier: str,
        host: str,
        port: str,
        password: str,
        resume_key: str | None = None,
        rest_url: str | None = None,
        ws_url: str | None = None,
        json_dumps: JSONDumps | None = None,
        json_loads: JSONLoads | None = None,
        session: aiohttp.ClientSession | None = None,
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> None:

        self._provider: Provider = provider
        self._bot: BotT = bot
        self._identifier: str = identifier

        self._host: str = host
        self._port: str = port
        self._password: str = password
        self._resume_key: str | None = resume_key

        # noinspection HttpUrlsUsage
        self._rest_url: str = rest_url or f"http://{host}:{port}"
        self._ws_url: str = ws_url or f"ws://{host}:{port}{'/magma' if provider is Provider.OBSIDIAN else ''}"

        self._json_dumps: JSONDumps = json_dumps or json.dumps
        self._json_loads: JSONLoads = json_loads or json.loads

        self._session: aiohttp.ClientSession = session or aiohttp.ClientSession()

        self._spotify: spotipy.Client | None = None
        if spotify_client_id and spotify_client_secret:
            self._spotify = spotipy.Client(client_id=spotify_client_id, client_secret=spotify_client_secret, session=self._session)

        self._websocket: aiohttp.ClientWebSocketResponse | None = None
        self._task: asyncio.Task[None] | None = None

        self._stats: Stats | None = None
        self._players: dict[int, PlayerT] = {}

    def __repr__(self) -> str:
        return "<slate.Node>"

    # Properties

    @property
    def provider(self) -> Provider:
        return self._provider

    @property
    def bot(self) -> BotT:
        return self._bot

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def resume_key(self) -> str | None:
        return self._resume_key

    @property
    def stats(self) -> Stats | None:
        return self._stats

    @property
    def players(self) -> dict[int, PlayerT]:
        return self._players

    # Utility methods

    def is_connected(self) -> bool:
        return self._websocket is not None and self._websocket.closed is False

    # Rest

    async def request(
        self,
        method: Literal["GET"], /,
        *,
        endpoint: str,
        parameters: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        url = f"{self._rest_url}{endpoint}"
        headers = {
            "Authorization": self._password,
            "Client-Name":   "Slate"
        }

        for tries in range(5):

            try:
                async with self._session.request(method, url=url, headers=headers, params=parameters, data=data) as response:

                    if 200 <= response.status < 300:
                        __log__.info(f"'{method}' @ '{response.url}' -> '{response.status}'")
                        return await response.json(loads=self._json_loads)

            except OSError as error:
                if tries >= 4 or error.errno not in (54, 10054):
                    raise

            delay = 1 + tries * 2

            __log__.info(f"'{method}' @ '{response.url}' -> '{response.status}', retrying in {delay}s.")  # type: ignore
            await asyncio.sleep(delay)

        message = f"'{method}' @ '{response.url}' -> '{response.status}', all five retries used."  # type: ignore

        __log__.info(message)
        raise HTTPError(response, message=message)  # type: ignore

    async def _search_spotify(
        self,
        id: str,
        type: str,
        ctx: ContextT | None = None,
    ) -> Search[ContextT]:

        assert self._spotify

        try:
            if type == "album":
                result = await self._spotify.get_full_album(id)
                tracks = result.tracks

            elif type == "playlist":
                result = await self._spotify.get_full_playlist(id)
                tracks = result.tracks

            elif type == "artist":
                result = await self._spotify.get_artist(id)
                tracks = await self._spotify.get_artist_top_tracks(id)

            else:  # type == "track"
                result = await self._spotify.get_track(id)
                tracks = [result]

        except spotipy.NotFound:
            raise NoResultsFound(search=id, source=Source.SPOTIFY, type=type)
        except spotipy.HTTPError:
            raise SearchFailed(data={"message": "Error while accessing spotify API.", "severity": "COMMON"})

        return Search(
            source=Source.SPOTIFY,
            type=type,
            result=result,
            tracks=[
                Track(
                    id="",
                    info={
                        "title":       track.name or "Unknown",
                        "author":      ", ".join(artist.name for artist in track.artists) if track.artists else "Unknown",
                        "uri":         track.url or "Unknown",
                        "identifier":  track.id or hash(
                            f"{track.name or 'Unknown'} - "
                            f"{', '.join(artist.name for artist in track.artists) if track.artists else 'Unknown'} - "
                            f"{track.duration_ms or 0}"
                        ),
                        "length":      track.duration_ms or 0,
                        "position":    0,
                        "is_stream":   False,
                        "is_seekable": False,
                        "source_name": "spotify",
                        "artwork_url": (result.images[0].url if result.images else None)
                                       if isinstance(result, spotipy.Album)
                                       else (track.album.images[0].url if track.album.images else None),  # type: ignore
                        "isrc":        getattr(track, "external_ids", {}).get("isrc") or None,
                    },
                    ctx=ctx
                ) for track in tracks
            ]
        )

    async def _search_other(
        self,
        search: str, /,
        *,
        source: Source = Source.NONE,
        ctx: ContextT | None = None,
    ) -> Search[ContextT]:

        if source is Source.YOUTUBE:
            identifier = f"ytsearch:{search}"
        elif source is Source.YOUTUBE_MUSIC:
            identifier = f"ytmsearch:{search}"
        elif source is Source.SOUNDCLOUD:
            identifier = f"scsearch:{search}"
        else:
            identifier = search

        data = await self.request("GET", endpoint="/loadtracks", parameters={"identifier": identifier})
        load_type = data["load_type" if "load_type" in data else "loadType"]

        if load_type in {"FAILED", "LOAD_FAILED"}:
            raise SearchFailed(data["exception"])

        elif load_type in {"NONE", "NO_MATCHES"}:
            raise NoResultsFound(search=search, source=source, type="track")

        elif load_type in {"TRACK", "TRACK_LOADED", "SEARCH_RESULT"}:

            tracks = [Track(id=track["track"], info=track["info"], ctx=ctx) for track in data["tracks"]]
            return Search(source=tracks[0].source, type="track", result=tracks, tracks=tracks)

        elif load_type in {"TRACK_COLLECTION", "PLAYLIST_LOADED"}:

            if self._provider is Provider.OBSIDIAN:
                info = data["collection_info"]
            else:
                info = data["playlistInfo"]
                info["url"] = search

            collection = Collection(info=info, tracks=data["tracks"], ctx=ctx)
            return Search(source=collection.source, type="collection", result=collection, tracks=collection.tracks)

        else:
            raise SearchFailed(data={"message": "Unknown '/loadtracks' load type.", "severity": "FAULT"})

    async def search(
        self,
        search: str,
        /,
        *,
        source: Source = Source.NONE,
        ctx: ContextT | None = None,
    ) -> Search[ContextT]:

        if self._spotify and (match := SPOTIFY_URL_REGEX.match(search)):
            return await self._search_spotify(id=match.group("id"), type=match.group("type"), ctx=ctx)

        return await self._search_other(search, source=source, ctx=ctx)

    # Websocket

    async def _listen(self) -> None:

        backoff = Backoff(max_time=60, max_tries=5)

        while True:

            assert isinstance(self._websocket, aiohttp.ClientWebSocketResponse)
            message = await self._websocket.receive()

            if message.type is aiohttp.WSMsgType.CLOSED:

                delay = backoff.calculate()
                __log__.warning(f"Node '{self._identifier}'s websocket was closed, attempting reconnection in {round(delay)} seconds.")

                await asyncio.sleep(delay)

                if not self._websocket or self._websocket.closed:
                    await self.connect()

                continue

            payload = message.json(loads=self._json_loads)
            asyncio.create_task(self._receive_payload(payload["op"], data=payload["d"] if "d" in payload else payload))

    async def _receive_payload(
        self,
        op: str | int, /,
        *,
        data: dict[str, Any]
    ) -> None:

        __log__.debug(f"Node '{self._identifier}' received a payload with op '{op}'.\nData: {data}")

        if op in (1, "stats"):
            self._stats = None  # Stats(data)
            return

        player = self._players.get(int(data["guild_id"] if self._provider is Provider.OBSIDIAN else data["guildId"]))

        if op in (4, "event"):

            if not player:
                __log__.warning(f"Node '{self._identifier}' received a player event for a guild without a player.\nData: {data}")
            else:
                player._dispatch_event(data)
            return

        if op in (5, "playerUpdate"):

            if not player:
                __log__.warning(f"Node '{self._identifier}' received a player update for a guild without a player.\nData: {data}")
            else:
                player._update_state(data)
            return

        __log__.warning(f"Node '{self._identifier}' received a payload with an unknown op '{op}'.\nData: {data}")

    async def _send_payload(
        self,
        op: int, /,
        *,
        data: dict[str, Any] | None = None,
        guild_id: str | None = None
    ) -> None:

        if not self._websocket or self._websocket.closed:
            raise NodeNotConnected(f"Node '{self._identifier}' is not connected.")

        if not data:
            data = {}

        if self._provider is Provider.OBSIDIAN:
            if guild_id:
                data["guild_id"] = guild_id
            data = {
                "op": op,
                "d": data
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
        __log__.debug(f"Node '{self._identifier}' sent a payload with op '{op}'.\nData: {data}")

    # Node methods

    async def connect(
        self,
        *,
        raise_on_fail: bool = True
    ) -> None:

        assert self._bot.user

        headers = {
            "Authorization": self._password,
            "User-Id":       str(self._bot.user.id),
            "Client-Name":   "Slate",
        }
        if self.resume_key:
            headers["Resume-Key"] = self.resume_key

        try:
            websocket = await self._session.ws_connect(url=self._ws_url, headers=headers)

        except Exception as error:

            if isinstance(error, aiohttp.WSServerHandshakeError) and error.status in (401, 4001):
                raise NodeInvalidPassword(f"Node '{self._identifier}' failed to connect due to an invalid password.")

            message = f"Node '{self._identifier}' failed to connect."
            __log__.error(message)

            if raise_on_fail:
                raise NodeConnectionError(message)

        else:

            self._websocket = websocket

            if self._task is None:
                self._task = asyncio.create_task(self._listen())

            if self._resume_key:
                await self._send_payload(
                    2,  # configureResuming
                    data={"key": self.resume_key, "timeout": 120}
                )

            self._bot.dispatch("slate_node_connected", self)
            __log__.info(f"Node '{self._identifier}' connected.")

    async def disconnect(
        self,
        *,
        force: bool = False
    ) -> None:

        for player in self._players.copy().values():
            await player.disconnect(force=force)

        if self._task and not self._task.done():
            self._task.cancel()

        self._task = None

        if self._websocket and not self._websocket.closed:
            await self._websocket.close()

        self._websocket = None

        self._bot.dispatch("slate_node_disconnected", self)
        __log__.info(f"Node '{self._identifier}' disconnected.")
