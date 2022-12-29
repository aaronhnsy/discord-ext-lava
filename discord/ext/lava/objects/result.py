from typing import TypeAlias

from .playlist import Playlist
from .track import Track
from ..types.common import SpotifySource


__all__ = ["Result"]

ResultSource: TypeAlias = SpotifySource | Playlist | list[Track] | Track


class Result:

    def __init__(
        self,
        *,
        source: ResultSource,
        tracks: list[Track],
    ) -> None:
        self.source: ResultSource = source
        self.tracks: list[Track] = tracks
