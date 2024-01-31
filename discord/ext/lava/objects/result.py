from collections.abc import Sequence

from ..types.common import SpotifySource
from .playlist import Playlist
from .track import Track


__all__ = ["Result"]


class Result:

    def __init__(
        self,
        *,
        source: SpotifySource | Playlist | Sequence[Track] | Track,
        tracks: Sequence[Track],
    ) -> None:
        self.source: SpotifySource | Playlist | Sequence[Track] | Track = source
        self.tracks: Sequence[Track] = tracks

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Result: source={self.source}>"
