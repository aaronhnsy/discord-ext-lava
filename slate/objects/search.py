from __future__ import annotations

import spotipy

from .collection import Collection
from .enums import Source
from .track import Track


__all__ = (
    "Search",
)

Result = spotipy.Album | spotipy.Playlist | spotipy.Artist | spotipy.Track | list[Track] | Collection


class Search:

    __slots__ = ("_source", "_type", "_result", "_tracks",)

    def __init__(
        self,
        *,
        source: Source,
        type: str,
        result: Result,
        tracks: list[Track]
    ) -> None:

        self._source: Source = source
        self._type: str = type
        self._result: Result = result
        self._tracks: list[Track] = tracks

    def __repr__(self) -> str:
        return f"<slate.Result source={self._source}, type='{self._type}', result={type(self._result)}>"

    # properties

    @property
    def source(self) -> Source:
        return self._source

    @property
    def type(self) -> str:
        return self._type

    @property
    def result(self) -> Result:
        return self._result

    @property
    def tracks(self) -> list[Track]:
        return self._tracks
