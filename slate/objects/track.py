# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import spotipy

# Local
from ..types import SpotifySearchResult, SpotifySearchTrack
from .enums import Source


__all__ = (
    "Track",
)


class Track:

    __slots__ = (
        "id",
        "title",
        "author",
        "uri",
        "identifier",
        "length",
        "position",
        "source",
        "_artwork_url",
        "isrc",
        "_is_stream",
        "_is_seekable",
        "extras",
    )

    def __init__(
        self,
        *,
        id: str,
        info: dict[str, Any],
        extras: dict[str, Any] | None = None,
    ) -> None:

        self.id: str = id

        self.title: str = info["title"]
        self.author: str = info["author"]
        self.uri: str = info["uri"]
        self.identifier: str = info["identifier"]
        self.length: int = info["length"]
        self.position: int = info["position"]
        self.source: Source = Source(info.get("source_name", info.get("sourceName", "Unknown")))
        self._artwork_url: str | None = info.get("artwork_url")
        self.isrc: str | None = info.get("isrc")

        self._is_stream: bool = info.get("is_stream", info.get("isStream", False))
        self._is_seekable: bool = info.get("is_seekable", info.get("isSeekable", False))

        self.extras: dict[str, Any] = extras or {}

    def __repr__(self) -> str:
        return f"<slate.Track title='{self.title}', author='{self.author}'>"

    # Properties

    @property
    def artwork_url(self) -> str | None:

        if self._artwork_url:
            return self._artwork_url
        elif self.source is Source.YOUTUBE:
            return f"https://img.youtube.com/vi/{self.identifier}/hqdefault.jpg"

        return None

    # Utilities

    def is_stream(self) -> bool:
        return self._is_stream

    def is_seekable(self) -> bool:
        return self._is_seekable

    # Classmethods

    @staticmethod
    def _from_spotify_track(
        track: SpotifySearchTrack,
        result: SpotifySearchResult,
        extras: dict[str, Any] | None = None
    ) -> Track:

        title = track.name or "Unknown"
        author = ", ".join(artist.name for artist in track.artists) if track.artists else "Unknown"
        length = track.duration_ms or 0

        # SimpleTrack's are only ever received when the
        # result is an Album. They don't have 'album' or
        # 'external_ids' attributes, so we have to fetch
        # those from the album instead.
        if isinstance(track, spotipy.SimpleTrack):
            assert isinstance(result, spotipy.Album)
            artwork_url = result.images[0].url if result.images else None
            isrc = None
        else:
            artwork_url = track.album.images[0].url if track.album.images else None
            isrc = track.external_ids.get("isrc")

        return Track(
            id="",
            info={
                "title":       title,
                "author":      author,
                "uri":         track.url or "Unknown",
                "identifier":  track.id or hash(f"{title} - {author} - {length}"),
                "length":      length,
                "position":    0,
                "source_name": "spotify",
                "artwork_url": artwork_url,
                "isrc":        isrc,
                "is_stream":   False,
                "is_seekable": False,
            },
            extras=extras
        )
