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
    InvalidNodePassword,
    NodeConnectionError,
    NodeNotConnected,
    NoResultsFound,
    SearchFailed,
)
from .objects.collection import Collection
from .objects.enums import Provider, Source
from .objects.search import Search
from .objects.track import Track
from .types import BotT, ContextT, JSONDumps, JSONLoads, PlayerT
from .utils import MISSING, OBSIDIAN_TO_LAVALINK_OP_MAP, SPOTIFY_URL_REGEX, Backoff


__all__ = (
    "Node",
)
__log__: logging.Logger = logging.getLogger("slate.node")


class Node(Generic[BotT, PlayerT]):
    """
    Node's handle interactions between your bot and a provider server such as obsidian or lavalink. This includes
    connecting to the websocket, searching for tracks, and managing player state.
    """

    def __init__(
        self,
        *,
        bot: BotT,
        session: aiohttp.ClientSession | None = None,
        # Connection information
        provider: Provider,
        identifier: str,
        host: str,
        port: str,
        password: str,
        secure: bool = False,
        resume_key: str | None = None,
        # URLs
        rest_url: str | None = None,
        ws_url: str | None = None,
        # JSON callables
        json_dumps: JSONDumps | None = None,
        json_loads: JSONLoads | None = None,
        # Spotify
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        bot
            The bot instance that this node belongs to.
        session
            The aiohttp client session to use for websocket/rest communication. Optional, if :class:`None` (default), a new one will be created.
        provider
            An enum denoting which external application this node is connecting to, such as :attr:`slate.Provider.OBSIDIAN`.
        identifier
            A unique identifier for this node.
        host
            The hostname of the provider server.
        port
            The port of the provider server.
        password
            The password for the provider server.
        secure
            Whether to use secure connections for websocket/rest communication. Optional, defaults to :obj:`False`.
        resume_key
            A resuming key which is passed to the provider server when connecting. Optional, defaults to :class:`None`.
        rest_url
            The URL to the provider server's REST API. Optional, if :class:`None` (default), the URL will be constructed from the provided host and port.
        ws_url
            The URL to the provider server's websocket. Optional, if :class:`None` (default), the URL will be constructed from the provided host and port.
        json_dumps
            A callable which will be used to serialize JSON data. Optional, if :class:`None` (default), :func:`json.dumps` will be used.
        json_loads
            A callable which will be used to deserialize JSON data. Optional, if :class:`None` (default), :func:`json.loads` will be used.
        spotify_client_id
            The client ID from a Spotify API application. Optional, if :class:`None` (default), Spotify integration will be disabled.
        spotify_client_secret
            The client secret from a Spotify API application. Optional, if :class:`None` (default), Spotify integration will be disabled.
        """

        self._bot: BotT = bot
        self._session: aiohttp.ClientSession | None = session

        self.provider: Provider = provider
        self.identifier: str = identifier
        self.host: str = host
        self.port: str = port
        self.password: str = password
        self.secure: bool = secure
        self.resume_key: str | None = resume_key

        self._rest_url: str | None = rest_url
        self._ws_url: str | None = ws_url

        self._json_dumps: JSONDumps = json_dumps or json.dumps
        self._json_loads: JSONLoads = json_loads or json.loads

        self._spotify: spotipy.Client | None = spotipy.Client(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            session=self._session
        ) if (spotify_client_id and spotify_client_secret) else None

        self._websocket: aiohttp.ClientWebSocketResponse | None = None
        self._task: asyncio.Task[None] | None = None

        self._players: dict[int, PlayerT] = {}

    def __repr__(self) -> str:
        return f"<slate.Node player_count={len(self.players)}>"

    # Properties

    @property
    def bot(self) -> BotT:
        """
        The bot instance that this node belongs to.
        """
        return self._bot

    @property
    def rest_url(self) -> str:
        """
        The URL used for rest requests to the provider server.
        """
        return self._rest_url or f"http://{self.host}:{self.port}"

    @property
    def ws_url(self) -> str:
        """
        The URL used to connect to the provider server's websocket.
        """
        return self._ws_url or f"ws://{self.host}:{self.port}{'/magma' if self.provider is Provider.OBSIDIAN else ''}"

    @property
    def players(self) -> dict[int, PlayerT]:
        """
        A mapping of guild ID to player instance.
        """
        return self._players

    # Utilities

    def is_connected(self) -> bool:
        """
        Returns :obj:`True` if the node is connected to the provider server, :obj:`False` otherwise.
        """
        return self._websocket is not None and self._websocket.closed is False

    # Connection

    async def connect(
        self,
        *,
        raise_on_failure: bool = False
    ) -> None:
        """
        Connects this node to its provider server.

        Arguments
        ---------
        raise_on_failure: bool
            Whether to raise an exception if the connection fails. Defaults to :obj:`False`.
        """

        assert self._bot.user is not None

        headers = {
            "Authorization": self.password,
            "User-Id":       str(self._bot.user.id),
            "Client-Name":   "Slate",
        }
        if self.resume_key:
            headers["Resume-Key"] = self.resume_key

        session = await self._get_session()

        try:
            websocket = await session.ws_connect(url=self.ws_url, headers=headers)

        except Exception as error:

            if isinstance(error, aiohttp.WSServerHandshakeError) and error.status in (401, 4001):
                raise InvalidNodePassword(f"Node '{self.identifier}' failed to connect due to an invalid password.")

            __log__.error((message := f"Node '{self.identifier}' failed to connect."))
            if raise_on_failure:
                raise NodeConnectionError(message)

        else:

            self._websocket = websocket

            if self._task is None:
                self._task = asyncio.create_task(self._listen())

            if self.resume_key:
                await self._send_payload(
                    2,  # configureResuming
                    data={
                        "key":     self.resume_key,
                        "timeout": 120
                    }
                )

            __log__.info(f"Node '{self.identifier}' connected.")

    async def disconnect(
        self,
        *,
        force: bool = False
    ) -> None:
        """
        Disconnects this node from its provider server.

        Parameters
        ----------
        force: bool
            Whether to force disconnect players with :meth:`Player.disconnect`. Defaults to :obj:`False`.
        """

        for player in self._players.copy().values():
            await player.disconnect(force=force)

        if self._task and not self._task.done():
            self._task.cancel()

        self._task = None

        if self._websocket and not self._websocket.closed:
            await self._websocket.close()

        self._websocket = None

        __log__.info(f"Node '{self.identifier}' disconnected.")

    # Rest

    async def _get_session(self) -> aiohttp.ClientSession:

        if not self._session:
            self._session = aiohttp.ClientSession()

        return self._session

    async def _request(
        self,
        method: Literal["GET"], /,
        *,
        path: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        session = await self._get_session()

        url = f"{self.rest_url}{path}"
        headers = {
            "Authorization": self.password,
            "Client-Name":   "Slate"
        }

        response: aiohttp.ClientResponse = MISSING

        for tries in range(5):

            try:
                async with session.request(
                        method,
                        url=url,
                        headers=headers,
                        params=parameters,
                ) as response:

                    if 200 <= response.status < 300:
                        __log__.info(f"'{method}' @ '{response.url}' -> '{response.status}'")
                        return await response.json(loads=self._json_loads)

            except OSError as error:
                if tries >= 4 or error.errno not in (54, 10054):
                    raise

            delay = 1 + tries * 2

            __log__.warning(f"'{method}' @ '{response.url}' -> '{response.status}', retrying in {delay}s.")
            await asyncio.sleep(delay)

        message = f"'{method}' @ '{response.url}' -> '{response.status}', all five retries used."

        __log__.error(message)
        raise HTTPError(response, message=message)

    async def _search_spotify(
        self,
        _id: str,
        _type: str,
        ctx: ContextT | None = None,
    ) -> Search[ContextT]:

        assert self._spotify

        try:
            if _type == "album":
                result = await self._spotify.get_full_album(_id)
                tracks = result.tracks

            elif _type == "playlist":
                result = await self._spotify.get_full_playlist(_id)
                tracks = result.tracks

            elif _type == "artist":
                result = await self._spotify.get_artist(_id)
                tracks = await self._spotify.get_artist_top_tracks(_id)

            else:  # _type == "track"
                result = await self._spotify.get_track(_id)
                tracks = [result]

        except spotipy.NotFound:
            raise NoResultsFound(search=_id, source=Source.SPOTIFY, type=_type)
        except spotipy.HTTPError:
            raise SearchFailed(data={"message": "Error while accessing spotify API.", "severity": "COMMON"})

        return Search(
            source=Source.SPOTIFY,
            type=_type,
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

        data = await self._request("GET", path="/loadtracks", parameters={"identifier": identifier})
        load_type = data["load_type" if "load_type" in data else "loadType"]

        if load_type in {"FAILED", "LOAD_FAILED"}:
            raise SearchFailed(data["exception"])

        elif load_type in {"NONE", "NO_MATCHES"}:
            raise NoResultsFound(search=search, source=source, type="track")

        elif load_type in {"TRACK", "TRACK_LOADED", "SEARCH_RESULT"}:

            tracks = [Track(id=track["track"], info=track["info"], ctx=ctx) for track in data["tracks"]]
            return Search(source=tracks[0].source, type="track", result=tracks, tracks=tracks)

        elif load_type in {"TRACK_COLLECTION", "PLAYLIST_LOADED"}:

            if self.provider is Provider.OBSIDIAN:
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
        search: str, /,
        *,
        source: Source = Source.NONE,
        ctx: ContextT | None = None,
    ) -> Search[ContextT]:
        """
        Requests search results from this node's provider server, or other services like spotify.

        Parameters
        ----------
        search
            The search query.
        source
            The source to request results from. Defaults to :attr:`Source.NONE`.
        ctx
            Adds extra data such as :attr:`Track.requester` to returned objects. Defaults to :class:`None`.

        Raises
        ------
        :exc:`~slate.NoResultsFound`
            If no results were found.
        :exc:`~slate.SearchFailed`
            If the search failed.
        :exc:`~slate.HTTPError`
            If the HTTP request failed.
        """

        if self._spotify and (match := SPOTIFY_URL_REGEX.match(search)):
            return await self._search_spotify(_id=match.group("id"), _type=match.group("type"), ctx=ctx)

        return await self._search_other(search, source=source, ctx=ctx)

    # Websocket

    async def _listen(self) -> None:

        backoff = Backoff(max_time=60, max_tries=5)

        while True:

            assert isinstance(self._websocket, aiohttp.ClientWebSocketResponse)
            message = await self._websocket.receive()

            if message.type is aiohttp.WSMsgType.CLOSED:

                delay = backoff.calculate()
                __log__.warning(f"Node '{self.identifier}'s websocket was closed, attempting reconnection in {round(delay)} seconds.")

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

        __log__.debug(f"Node '{self.identifier}' received a payload with op '{op}'.\nData: {data}")

        if op in (1, "stats"):
            self._stats = None  # Stats(data)
            return

        player = self._players.get(int(data["guild_id"] if self.provider is Provider.OBSIDIAN else data["guildId"]))

        if op in (4, "event"):

            if not player:
                __log__.warning(f"Node '{self.identifier}' received a player event for a guild without a player.\nData: {data}")
            else:
                player._dispatch_event(data)
            return

        if op in (5, "playerUpdate"):

            if not player:
                __log__.warning(f"Node '{self.identifier}' received a player update for a guild without a player.\nData: {data}")
            else:
                player._update_state(data)
            return

        __log__.warning(f"Node '{self.identifier}' received a payload with an unknown op '{op}'.\nData: {data}")

    async def _send_payload(
        self,
        op: int, /,
        *,
        data: dict[str, Any] | None = None,
        guild_id: str | None = None
    ) -> None:

        if not self._websocket or self._websocket.closed:
            raise NodeNotConnected(f"Node '{self.identifier}' is not connected.")

        if not data:
            data = {}

        if self.provider is Provider.OBSIDIAN:
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
        __log__.debug(f"Node '{self.identifier}' sent a payload with op '{op}'.\nData: {data}")
