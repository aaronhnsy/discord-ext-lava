from .types.playlist import PlaylistData


__all__ = ["Playlist"]


class Playlist:

    __slots__ = ("name", "selected_track",)

    def __init__(self, data: PlaylistData) -> None:
        self.name: str = data["name"]
        self.selected_track: int = data["selectedTrack"]