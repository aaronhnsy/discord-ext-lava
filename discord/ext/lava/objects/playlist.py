from .types.playlist import PlaylistInfoData


__all__ = ["PlaylistInfo"]


class PlaylistInfo:

    __slots__ = ("name", "selected_track",)

    def __init__(self, data: PlaylistInfoData) -> None:
        self.name: str = data["name"]
        self.selected_track: int = data["selectedTrack"]
