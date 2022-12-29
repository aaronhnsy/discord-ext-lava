from __future__ import annotations

import discord.utils
import spotipy

from .types.track import TrackData
from ..types.common import SpotifySource


__all__ = ["Track"]


class Track:

    __slots__ = (
        "encoded", "identifier", "_is_seekable", "author", "length", "_is_stream", "position", "title", "uri",
        "artwork_url", "isrc", "source_name", "extras",
    )

    def __init__(self, data: TrackData) -> None:
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

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Track identifier='{self.identifier}', title='{self.title}', " \
               f"author='{self.author}', length={self.length}>"

    # utility methods

    def is_seekable(self) -> bool:
        return self._is_seekable

    def is_stream(self) -> bool:
        return self._is_stream

    # spotify

    @classmethod
    def _from_spotify_track(
        cls,
        source: SpotifySource,
        track: spotipy.SimpleTrack | spotipy.Track | spotipy.PlaylistTrack,
    ) -> Track:

        title = track.name or "Unknown"
        author = ", ".join(artist.name for artist in track.artists) if track.artists else "Unknown"

        # SimpleTrack's are received when an album is fetched, they don't have the
        # 'album' or 'external_ids' attributes so the artworkUrl must be fetched
        # from the album result itself. Unfortunately this also means you can't
        # get an isrc for these tracks.
        if isinstance(track, spotipy.SimpleTrack):
            assert isinstance(source, spotipy.Album)
            artwork_url = source.images[0].url if source.images else None
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
            }
        )
