# Local Folder
from ..types.objects.playlist import PlaylistData, PlaylistInfoData
from .track import Track


__all__ = ["Playlist"]


class Playlist:
    __slots__ = ("name", "selected_track", "tracks",)

    def __init__(self, data: PlaylistData) -> None:
        info: PlaylistInfoData = data["info"]
        self.name: str = info["name"]
        self.selected_track: int = info["selectedTrack"]
        self.tracks: list[Track] = [Track(track) for track in data["tracks"]]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Playlist name='{self.name}', selected_track={self.selected_track}>"
