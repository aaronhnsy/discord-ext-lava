# Future
from __future__ import annotations

# Standard Library
import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar, Union

# Packages
import aiohttp
import aiospotify
import discord
from discord.ext import commands

# My stuff
from slate import utils
from slate.exceptions import (
    NodeAlreadyExists,
    NodeConnectionError,
    NodeNotConnected,
    NodeNotFound,
    NodesNotFound,
    NoMatchesFound,
)
from slate.node import BaseNode
from slate.objects.enums import LoadType, SearchType, Source
from slate.obsidian.exceptions import SearchError
from slate.obsidian.objects.enums import Op
from slate.obsidian.objects.playlist import Playlist
from slate.obsidian.objects.search import SearchResult
from slate.obsidian.objects.stats import Stats
from slate.obsidian.objects.track import Track
from slate.utils import ExponentialBackoff


if TYPE_CHECKING:

    # My stuff
    from slate.obsidian.player import Player


__all__ = (
    "NodePool",
    "Node"
)
__log__: logging.Logger = logging.getLogger("slate.obsidian.node")


BotT = TypeVar("BotT", bound=Union[discord.Client, discord.AutoShardedClient, commands.Bot, commands.AutoShardedBot])
ContextT = TypeVar("ContextT", bound=commands.Context)
PlayerT = TypeVar("PlayerT", bound="Player")


class NodePool(Generic[BotT, ContextT, PlayerT]):

    nodes: dict[str, Node[BotT, ContextT, PlayerT]] = {}

    def __repr__(self) -> str:
        return f"<slate.obsidian.NodePool>"

    #

    @classmethod
    async def create_node(
        cls,
        *,
        bot: BotT,
        identifier: str,
        host: str,
        port: str,
        password: str,
        session: aiohttp.ClientSession | None = None,
        json_dumps: Callable[[], str] | None = None,
        json_loads: Callable[[], dict[str, Any]] | None = None,
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> Node[BotT, ContextT, PlayerT]:

        if identifier in cls.nodes:
            raise NodeAlreadyExists(f"Node with identifier '{identifier}' already exists.")

        node = Node(
            bot,
            identifier,
            host,
            port,
            password,
            session,
            json_dumps,
            json_loads,
            spotify_client_id,
            spotify_client_secret,
        )
        await node.connect()

        cls.nodes[node._identifier] = node
        return node

    @classmethod
    def get_node(
        cls,
        *,
        identifier: str | None = None
    ) -> Node[BotT, ContextT, PlayerT]:

        if not cls.nodes:
            raise NodesNotFound("There are no nodes connected.")

        if identifier:

            if not (node := cls.nodes.get(identifier)):
                raise NodeNotFound(f"A node with identifier '{identifier}' was not found.")

            return node

        return list(cls.nodes.values())[0]


class Node(BaseNode, Generic[BotT, ContextT, PlayerT]):

    def __init__(
        self,
        bot: BotT,
        identifier: str,
        host: str,
        port: str,
        password: str,
        session: aiohttp.ClientSession | None = None,
        json_dumps: Callable[[], str] | None = None,
        json_loads: Callable[[], dict[str, Any]] | None = None,
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> None:

        super().__init__(
            bot,
            identifier,
            host,
            port,
            password,
            session,
            json_dumps,
            json_loads,
            spotify_client_id,
            spotify_client_secret,
        )

        self._players: dict[int, PlayerT[BotT, ContextT, PlayerT]] = {}
        self._stats: Stats | None = None

    def __repr__(self) -> str:
        return f"<slate.obsidian.Node>"

    #

    @property
    def _http_url(self) -> str:
        return f"http://{self._host}:{self._port}/"

    @property
    def _ws_url(self) -> str:
        return f"ws://{self._host}:{self._port}/magma"

    @property
    def players(self) -> dict[int, PlayerT[BotT, ContextT, PlayerT]]:
        return self._players

    @property
    def stats(self) -> Stats | None:
        return self._stats

    #

    async def connect(
        self,
        *,
        raise_on_fail: bool = True
    ) -> None:

        try:
            websocket = await self._session.ws_connect(
                url=self._ws_url,
                headers={
                    "Authorization": self._password,
                    "User-Id":       str(self._bot.user.id),
                    "Client-Name":   "Slate",
                }
            )

        except Exception:

            message = f"Node '{self._identifier}' failed to connect."

            __log__.error(message)
            if raise_on_fail:
                raise NodeConnectionError(message)

        else:

            self._websocket = websocket

            if self._task is None:
                self._task = asyncio.create_task(self._listen())

            self._bot.dispatch("obsidian_node_connected", self)
            __log__.info(f"Node '{self._identifier}' has been connected.")

    async def disconnect(
        self,
        *,
        force: bool = False
    ) -> None:

        for player in self._players.copy().values():
            await player.disconnect(force=force)

        if self._websocket and not self._websocket.closed:
            await self._websocket.close()

        self._websocket = None

        if self._task and not self._task.done:
            self._task.cancel()

        self._task = None

        self._bot.dispatch("obsidian_node_disconnected", self)
        __log__.info(f"Node '{self._identifier}' has been disconnected.")

    async def destroy(
        self,
        *,
        force: bool = False
    ) -> None:

        await self.disconnect(force=force)
        del NodePool.nodes[self._identifier]

        __log__.info(f"Node '{self._identifier}' has been destroyed.")

    async def _listen(
        self
    ) -> None:

        backoff = ExponentialBackoff(base=5)

        while True:

            assert isinstance(self._websocket, aiohttp.ClientWebSocketResponse)
            payload = await self._websocket.receive()

            if payload.type is aiohttp.WSMsgType.CLOSED:

                retry = backoff.delay()
                __log__.warning(f"Node '{self._identifier}'s websocket was closed, attempting reconnection in {round(retry)} seconds.")

                await asyncio.sleep(retry)

                if not (self._websocket and not self._websocket.closed):
                    await self.connect()

            else:
                asyncio.create_task(self._handle_payload(payload.json()))

    async def _handle_payload(
        self,
        payload: dict[str, Any],
        /
    ) -> None:

        try:
            op = Op(payload["op"])
        except ValueError:
            __log__.warning(f"Node '{self._identifier}' received payload with unknown op code.\nPayload: {payload}")
            return

        __log__.debug(f"Node '{self._identifier}' received payload with op {op!r}.\nPayload: {payload}")

        data = payload["d"]

        if op is Op.STATS:
            self._stats = Stats(data)
            return

        if not (player := self._players.get(int(data["guild_id"]))):
            return

        if op is Op.PLAYER_EVENT:
            player._dispatch_event(data)
        elif op is Op.PLAYER_UPDATE:
            player._update_state(data)

    async def _send_payload(
        self,
        op: Op,
        /,
        *,
        data: dict[str, Any]
    ) -> None:

        if not (self._websocket and not self._websocket.closed):
            raise NodeNotConnected(f"Node '{self._identifier}' is not connected.")

        payload = {
            "op": op.value,
            "d":  data
        }

        json = self._json_dumps(payload)
        if isinstance(json, bytes):
            json = json.decode("utf-8")

        await self._websocket.send_str(json)
        __log__.debug(f"Node '{self._identifier}' dispatched payload with {op!r}.\nPayload: {payload}")

    # Searching

    async def search(
        self,
        search: str,
        /,
        *,
        source: Source = Source.YOUTUBE,
        ctx: ContextT | None = None,
    ) -> SearchResult[ContextT]:

        if (match := utils.SPOTIFY_URL_REGEX.match(search)) and self._spotify is not None:

            search_type = SearchType(match.group("type"))
            spotify_id = match.group("id")

            try:
                if search_type is SearchType.ALBUM:
                    result = await self._spotify.get_full_album(spotify_id)
                    search_tracks = result.tracks

                elif search_type is SearchType.PLAYLIST:
                    result = await self._spotify.get_full_playlist(spotify_id)
                    search_tracks = result.tracks

                elif search_type is SearchType.ARTIST:
                    result = await self._spotify.get_artist(spotify_id)
                    search_tracks = await self._spotify.get_artist_top_tracks(spotify_id)

                else:
                    result = await self._spotify.get_track(spotify_id)
                    search_tracks = [result]

                if not search_tracks:
                    raise NoMatchesFound(search=search, search_type=search_type, source=Source.SPOTIFY)

            except aiospotify.NotFound:
                raise NoMatchesFound(search=search, search_type=search_type, source=Source.SPOTIFY)
            except aiospotify.SpotifyHTTPError:
                raise SearchError({"message": "Error while accessing spotify API.", "severity": "COMMON"})

            tracks = [
                Track(
                    ctx=ctx, id="",
                    info={
                        "title":       track.name or "UNKNOWN",
                        "author":      ", ".join(artist.name for artist in track.artists) if track.artists else "UNKNOWN",
                        "uri":         track.url or search,
                        "identifier":  track.id or "UNKNOWN",
                        "length":      track.duration_ms or 0,
                        "position":    0,
                        "is_stream":   False,
                        "is_seekable": False,
                        "source_name": "spotify",
                        "thumbnail":   track.album.images[0].url if (track.album and track.album.images) else None
                    }
                ) for track in search_tracks
            ]

            return SearchResult(source=Source.SPOTIFY, type=search_type, result=result, tracks=tracks)

        else:

            if source is Source.YOUTUBE:
                search = f"ytsearch:{search}"
            elif source is Source.SOUNDCLOUD:
                search = f"scsearch:{search}"
            elif source is Source.YOUTUBE_MUSIC:
                search = f"ytmsearch:{search}"

            data = await self.request("GET", endpoint="/loadtracks", parameters={"identifier": search})

            load_type = LoadType(data["load_type"])
            message = f"Node '{self._identifier}' received {load_type!r}' for search: {search}.\nData: {data}"

            if load_type is LoadType.LOAD_FAILED:
                __log__.warning(message)
                raise SearchError(data["exception"])

            if load_type is LoadType.NO_MATCHES or not data["tracks"]:
                __log__.info(message)
                raise NoMatchesFound(search=search, search_type=SearchType.TRACK, source=source)

            if load_type is LoadType.PLAYLIST_LOADED:

                __log__.info(message)

                info = data["playlist_info"]
                info["uri"] = search

                playlist = Playlist(info=info, tracks=data["tracks"], ctx=ctx)
                return SearchResult(source=playlist.source, type=SearchType.PLAYLIST, result=playlist, tracks=playlist.tracks)

            if load_type in [LoadType.TRACK_LOADED, LoadType.SEARCH_RESULT]:

                __log__.info(message)

                tracks = [Track(id=track["track"], info=track["info"], ctx=ctx) for track in data["tracks"]]
                return SearchResult(source=tracks[0].source, type=SearchType.TRACK, result=tracks, tracks=tracks)
