from .track import Track
from ..types.common import SpotifyResult


__all__: list[str] = ["Search"]


class Search:

    def __init__(
        self,
        *,
        result: SpotifyResult,
        tracks: list[Track],
    ) -> None:
        self.result: SpotifyResult = result
        self.tracks: list[Track] = tracks
