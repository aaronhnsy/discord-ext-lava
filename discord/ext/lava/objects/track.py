from __future__ import annotations

from typing import Generic, TypedDict, cast

import discord.utils
import spotipy
from typing_extensions import TypeVar

from ..types.common import SpotifyResult, SpotifyTrack
from ..types.objects.track import TrackData


__all__: list[str] = ["Track"]

TrackExtrasT = TypeVar("TrackExtrasT", bound=TypedDict, default=TypedDict)


class Track(Generic[TrackExtrasT]):

    __slots__ = (
        "encoded", "identifier", "_is_seekable", "author", "length", "_is_stream",
        "position", "title", "uri", "artwork_url", "isrc", "source_name", "extras"
    )

    def __init__(self, data: TrackData, *, extras: TrackExtrasT | None = None) -> None:
        self.encoded: str = data["encoded"]

        info = data["info"]
        self.identifier: str = info["identifier"]
        self.author: str = info["author"]
        self.length: int = info["length"]
        self.position: int = info["position"]
        self.title: str = info["title"]
        self.uri: str | None = info["uri"]
        self.artwork_url: str | None = info["artworkUrl"]
        self.isrc: str | None = info["isrc"]
        self.source_name: str = info["sourceName"]

        self._is_seekable: bool = info["isSeekable"]
        self._is_stream: bool = info["isStream"]

        self.extras: TrackExtrasT = extras or cast(TrackExtrasT, {})

    def __repr__(self) -> str:
        return f"discord.ext.lava.Track identifier='{self.identifier}', title='{self.title}', " \
               f"author='{self.author}', length={self.length}>"

    # utilities

    def is_seekable(self) -> bool:
        return self._is_seekable

    def is_stream(self) -> bool:
        return self._is_stream

    # spotify

    @classmethod
    def _from_spotify_track(
        cls,
        result: SpotifyResult,
        track: SpotifyTrack,
        extras: TrackExtrasT | None = None,
    ) -> Track:

        title = track.name or "Unknown"
        author = ", ".join(artist.name for artist in track.artists) if track.artists else "Unknown"

        # SimpleTrack's are received when an album is fetched, they don't have the
        # 'album' or 'external_ids' attributes so the artworkUrl must be fetched
        # from the album result itself. Unfortunately this also means you can't
        # get an isrc for these tracks.
        if isinstance(track, spotipy.SimpleTrack):
            assert isinstance(result, spotipy.Album)
            artwork_url = result.images[0].url if result.images else None
            isrc = None
        else:
            artwork_url = track.album.images[0].url if track.album.images else None
            isrc = track.external_ids.get("isrc")

        return Track(
            {
                "encoded": discord.utils.MISSING,
                "info":    {
                    "identifier": track.id or str(hash(f"{title} - {author} - {track.duration_ms}")),
                    "isSeekable": True,
                    "author":     author,
                    "length":     track.duration_ms,
                    "isStream":   False,
                    "position":   0,
                    "title":      title,
                    "uri":        track.uri,
                    "artworkUrl": artwork_url,
                    "isrc":       isrc,
                    "sourceName": "spotify",
                }
            },
            extras=extras
        )
