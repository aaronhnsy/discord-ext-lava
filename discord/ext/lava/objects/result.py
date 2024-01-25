from collections.abc import Sequence

from .playlist import Playlist
from .track import Track
from ..types.common import SpotifySource


__all__ = ["Result"]


type ResultSource = SpotifySource | Playlist | Sequence[Track] | Track


class Result:

    def __init__(
        self,
        *,
        source: ResultSource,
        tracks: Sequence[Track],
    ) -> None:
        self.source: ResultSource = source
        self.tracks: Sequence[Track] = tracks

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Result source={self.source}>"
