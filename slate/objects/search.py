# Future
from __future__ import annotations

# Packages
import spotipy

# Local
from .collection import Collection
from .enums import Source
from .track import Track


__all__ = (
    "Search",
)

Result = spotipy.Album | spotipy.Playlist | spotipy.Artist | spotipy.Track | list[Track] | Collection


class Search:

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

    # Properties

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
