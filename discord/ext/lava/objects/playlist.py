from .types.playlist import PlaylistData


__all__ = ["Playlist"]


class Playlist:

    __slots__ = ("name", "selected_track",)

    def __init__(self, data: PlaylistData) -> None:
        self.name: str = data["name"]
        self.selected_track: int = data["selectedTrack"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Playlist name='{self.name}', selected_track={self.selected_track}>"