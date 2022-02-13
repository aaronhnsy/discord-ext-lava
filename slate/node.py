# Future
from __future__ import annotations

# Standard Library
import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any, Callable, Generic, Literal, TypeVar, Union

# Packages
import aiohttp
import discord
import spotipy
from discord.ext import commands

# My stuff
from .exceptions import (
    HTTPError,
    NodeConnectionError,
    NodeInvalidPassword,
    NodeNotConnected,
    NoResultsFound,
    SearchFailed,
)
from .objects.collection import Collection
from .objects.enums import NodeType, Source
from .objects.result import Result
from .objects.stats import Stats
from .objects.track import Track
from .utils import SPOTIFY_URL_REGEX, ExponentialBackoff


if TYPE_CHECKING:
    # My stuff
    from .player import Player


__all__ = (
    "Node",
)
__log__: logging.Logger = logging.getLogger("slate.node")


BotT = TypeVar("BotT", bound=Union[discord.Client, discord.AutoShardedClient, commands.Bot, commands.AutoShardedBot])
ContextT = TypeVar("ContextT", bound=commands.Context)
PlayerT = TypeVar("PlayerT", bound="Player")  # type: ignore


class Node(Generic[BotT, ContextT, PlayerT]):

    def __init__(
        self,
        type: NodeType,
        bot: BotT,
        identifier: str,
        host: str,
        port: str,
        password: str,
        resume_key: str | None = None,
        rest_url: str | None = None,
        ws_url: str | None = None,
        json_dumps: Callable[..., str] | None = None,
        json_loads: Callable[..., dict[str, Any]] | None = None,
        session: aiohttp.ClientSession | None = None,
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> None:

        self._type: NodeType = type
        self._bot: BotT = bot
        self._identifier: str = identifier

        self._host: str = host
        self._port: str = port
        self._password: str = password
        self._resume_key: str | None = resume_key

        self._rest_url: str = rest_url or f"http://{host}:{port}"
        self._ws_url: str = ws_url or f"ws://{host}:{port}{'/magma' if type is NodeType.OBSIDIAN else ''}"

        self._json_dumps: Callable[..., str] = json_dumps or json.dumps
        self._json_loads: Callable[..., dict[str, Any]] = json_loads or json.loads

        self._session: aiohttp.ClientSession = session or aiohttp.ClientSession()

        self._spotify: spotipy.Client | None = None
        if spotify_client_id and spotify_client_secret:
            self._spotify = spotipy.Client(client_id=spotify_client_id, client_secret=spotify_client_secret, session=self._session)

        self._websocket: aiohttp.ClientWebSocketResponse | None = None
        self._task: asyncio.Task | None = None

        self._stats: Stats | None = None
        self._players: dict[int, PlayerT] = {}

    def __repr__(self) -> str:
        return "<slate.Node>"

    # Properties / Utilities

    @property
    def type(self) -> NodeType:
        return self._type

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
        id: str, /,
        *,
        type: str,
        ctx: ContextT | None = None,
    ) -> Result[ContextT]:

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
            raise SearchFailed({"message": "Error while accessing spotify API.", "severity": "COMMON"})

        return Result(
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
                                       else (track.album.images[0].url if track.album.images else None),
                        "isrc":        getattr(track, "external_ids", {}).get("isrc") or None,
                    },
                    ctx=ctx
                ) for track in tracks
            ]
        )

    async def _search_obsidian(
        self,
        search: str,
        /,
        *,
        source: Source = Source.NONE,
        ctx: ContextT | None = None,
    ) -> Result[ContextT]:

        if source is Source.YOUTUBE:
            identifier = f"ytsearch:{search}"
        elif source is Source.YOUTUBE_MUSIC:
            identifier = f"ytmsearch:{search}"
        elif source is Source.SOUNDCLOUD:
            identifier = f"scsearch:{search}"
        else:
            identifier = search

        data = await self.request("GET", endpoint="/loadtracks", parameters={"identifier": identifier})
        load_type = data["load_type"]

        if load_type == "FAILED":
            raise SearchFailed(data["exception"])

        elif load_type == "NONE":
            raise NoResultsFound(search=search, source=source, type="track")

        elif load_type == "TRACK":

            track = Track(id=data["tracks"][0]["track"], info=data["tracks"][0]["info"], ctx=ctx)
            return Result(source=track.source, type="track", result=track, tracks=[track])

        elif load_type == "TRACK_COLLECTION":

            collection = Collection(info=data["collection_info"], tracks=data["tracks"], ctx=ctx)
            return Result(source=collection.source, type=collection.type, result=collection, tracks=collection.tracks)

        else:
            raise SearchFailed({"message": "Unknown '/loadtracks' load type.", "severity": "FAULT"})

    async def _search_lavalink(
        self,
        search: str,
        /,
        *,
        source: Source = Source.NONE,
        ctx: ContextT | None = None,
    ) -> Result[ContextT]:

        if source is Source.YOUTUBE:
            identifier = f"ytsearch:{search}"
        elif source is Source.YOUTUBE_MUSIC:
            identifier = f"ytmsearch:{search}"
        elif source is Source.SOUNDCLOUD:
            identifier = f"scsearch:{search}"
        else:
            identifier = search

        data = await self.request("GET", endpoint="/loadtracks", parameters={"identifier": identifier})
        load_type = data["loadType"]

        if load_type == "LOAD_FAILED":
            raise SearchFailed(data["exception"])

        elif load_type == "NO_MATCHES":
            raise NoResultsFound(search=search, source=source, type="track")

        elif load_type in ("SEARCH_RESULT", "TRACK_LOADED"):

            track = Track(id=data["tracks"][0]["track"], info=data["tracks"][0]["info"], ctx=ctx)
            return Result(source=track.source, type="track", result=track, tracks=[track])

        elif load_type == "PLAYLIST_LOADED":

            collection = Collection(info=data["playlistInfo"], tracks=data["tracks"], ctx=ctx)
            collection._url = search

            return Result(source=collection.source, type=collection.type, result=collection, tracks=collection.tracks)

        else:
            raise SearchFailed({"message": "Unknown '/loadtracks' load type.", "severity": "FAULT"})

    async def search(
        self,
        search: str,
        /,
        *,
        source: Source = Source.NONE,
        ctx: ContextT | None = None,
    ) -> Result[ContextT]:

        if self._spotify and (match := SPOTIFY_URL_REGEX.match(search)):
            return await self._search_spotify(match.group("id"), type=match.group("type"), ctx=ctx)

        if self._type is NodeType.OBSIDIAN:
            return await self._search_obsidian(search, source=source, ctx=ctx)
        else:
            return await self._search_lavalink(search, source=source, ctx=ctx)

    # Websocket

    async def connect(self, *, raise_on_error: bool = True) -> None:

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

            if raise_on_error:
                raise NodeConnectionError(message)

        else:

            self._websocket = websocket

            if self._task is None:
                self._task = asyncio.create_task(self._listen())

            if self._resume_key:
                await self._send_payload(
                    2 if self._type is NodeType.OBSIDIAN else "configureResuming",
                    data={"key": self.resume_key, "timeout": 120}
                )

            self._bot.dispatch("slate_node_connected", self)
            __log__.info(f"Node '{self._identifier}' connected.")

    async def disconnect(self, *, force: bool = False) -> None:

        for player in self._players.copy().values():
            await player.disconnect(force=force)

        if self._task and not self._task.done:
            self._task.cancel()

        self._task = None

        if self._websocket and not self._websocket.closed:
            await self._websocket.close()

        self._websocket = None

        self._bot.dispatch("slate_node_disconnected", self)
        __log__.info(f"Node '{self._identifier}' disconnected.")

    async def _listen(
        self
    ) -> None:

        backoff = ExponentialBackoff(base=4)

        while True:

            assert isinstance(self._websocket, aiohttp.ClientWebSocketResponse)
            payload = await self._websocket.receive()

            if payload.type is aiohttp.WSMsgType.CLOSED:

                retry = backoff.delay()
                __log__.warning(f"Node '{self._identifier}'s websocket was closed, attempting reconnection in {round(retry)} seconds.")

                await asyncio.sleep(retry)

                if not self._websocket or self._websocket.closed:
                    await self.connect()

            else:
                asyncio.create_task(self._handle_payload(payload.json(loads=self._json_loads)))

    async def _handle_payload(
        self,
        payload: dict[str, Any], /
    ) -> None:

        op = payload["op"]
        data = payload["d"] if self._type is NodeType.OBSIDIAN else payload

        __log__.debug(f"Node '{self._identifier}' received a payload with op '{op}'.\nPayload: {data}")

        if op in (1, "stats"):  # Stats
            # self._stats = Stats(data)
            return

        player = self._players.get(int(data["guild_id"] if self._type is NodeType.OBSIDIAN else data["guildId"]))
        if not player:
            __log__.warning(f"Node '{self._identifier}' received a payload for a guild without a voice client.\nPayload: {payload}")
            return

        if op in (4, "event"):
            player._dispatch_event(data)
            return

        if op in (5, "playerUpdate"):
            player._update_state(data)
            return

        __log__.warning(f"Node '{self._identifier}' received a payload with an unknown op '{op}'.\nPayload: {payload}")

    async def _send_payload(
        self,
        op: int | str, /,
        *, data: dict[str, Any]
    ) -> None:

        if not self._websocket or self._websocket.closed:
            raise NodeNotConnected(f"Node '{self._identifier}' is not connected.")

        if self._type is NodeType.OBSIDIAN:
            payload = {
                "op": op,
                "d": data
            }
        else:
            payload = {
                "op": op,
                **data
            }

        _json = self._json_dumps(payload)
        if isinstance(_json, bytes):
            _json = _json.decode("utf-8")

        await self._websocket.send_str(_json)
        __log__.debug(f"Node '{self._identifier}' sent a payload with op '{op}'.\nPayload: {payload}")
