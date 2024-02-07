from __future__ import annotations

import spotipy

from .._utilities import MISSING
from ..types.objects.track import TrackData, TrackInfoData, TrackPluginInfoData, TrackUserData


__all__ = ["Track"]


class Track:
    __slots__ = (
        "encoded", "identifier", "_is_seekable", "author", "length", "_is_stream", "position", "title", "uri",
        "artwork_url", "isrc", "source", "plugin_info", "user_data",
    )

    def __init__(self, data: TrackData) -> None:
        # encoded track
        self.encoded: str = data["encoded"]
        # track info
        info: TrackInfoData = data["info"]
        self.identifier: str = info["identifier"]
        self._is_seekable: bool = info["isSeekable"]
        self.author: str = info["author"]
        self.length: int = info["length"]
        self._is_stream: bool = info["isStream"]
        self.position: int = info["position"]
        self.title: str = info["title"]
        self.uri: str | None = info["uri"]
        self.artwork_url: str | None = info["artworkUrl"]
        self.isrc: str | None = info["isrc"]
        self.source: str = info["sourceName"]
        # others
        self.plugin_info: TrackPluginInfoData = data["pluginInfo"]
        self.user_data: TrackUserData = data["userData"]

    def __repr__(self) -> str:
        return f"<lava.{self.__class__.__name__}: identifier='{self.identifier}', title='{self.title}', " \
               f"author='{self.author}', length={self.length}>"

    # utility methods

    def is_seekable(self) -> bool:
        return self._is_seekable

    def is_stream(self) -> bool:
        return self._is_stream

    # spotify

    @classmethod
    def _from_spotify_track(cls, track: spotipy.Track | spotipy.PlaylistTrack) -> Track:
        if track.is_local:
            identifier = track.uri
            author = track.artists[0].name or "Unknown"
            title = track.name or "Unknown"
            artwork_url = None
            isrc = None
        else:
            identifier = track.id
            author = ", ".join(artist.name for artist in track.artists)
            title = track.name
            artwork_url = track.album.images[0].url if len(track.album.images) > 0 else None
            isrc = track.external_ids.get("isrc")
        return Track(
            {
                "encoded":    MISSING,
                "info":       {
                    "identifier": identifier,
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
                },
                "pluginInfo": {},
                "userData":   {},
            }
        )
