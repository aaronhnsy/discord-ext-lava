from __future__ import annotations

from typing import TYPE_CHECKING

from .track import Track


if TYPE_CHECKING:
    from ..types.objects.playlist import PlaylistData


__all__ = ["Playlist"]


class Playlist:
    __slots__ = ("name", "selected_track", "tracks",)

    def __init__(self, data: PlaylistData) -> None:
        info = data["info"]
        self.name: str = info["name"]
        self.selected_track: int = info["selectedTrack"]
        self.tracks: list[Track] = [Track(track) for track in data["tracks"]]

    def __repr__(self) -> str:
        return f"<lava.{self.__class__.__name__}: name='{self.name}', selected_track={self.selected_track}>"
