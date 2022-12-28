from .playlist import PlaylistInfo
from .track import Track
from ..types.common import SpotifyResult


__all__ = ["Search"]


class Search:

    def __init__(
        self,
        *,
        result: SpotifyResult | PlaylistInfo,
        tracks: list[Track],
    ) -> None:
        self.result: SpotifyResult | PlaylistInfo = result
        self.tracks: list[Track] = tracks
