from __future__ import annotations

from typing import Any

from .enums import Source
from .track import Track


__all__ = (
    "Collection",
)


class Collection:

    __slots__ = ("_name", "_url", "_selected_track", "_tracks",)

    def __init__(
        self,
        *,
        info: dict[str, Any],
        tracks: list[dict[str, Any]],
        extras: dict[str, Any] | None = None,
    ) -> None:

        self._name: str = info["name"]
        self._url: str = info["url"]
        self._selected_track: int | None = info.get("selected_track") or info.get("selectedTrack")

        self._tracks: list[Track] = [Track(id=track["track"], info=track["info"], extras=extras) for track in tracks]

    def __repr__(self) -> str:
        return "<slate.Collection>"

    # properties

    @property
    def name(self) -> str:
        return self._name

    @property
    def url(self) -> str:
        return self._url

    @property
    def selected_track(self) -> Track | int | None:

        if not self._selected_track:
            return None

        try:
            return self._tracks[self._selected_track]
        except IndexError:
            return self._selected_track

    @property
    def tracks(self) -> list[Track]:
        return self._tracks

    @property
    def source(self) -> Source:

        try:
            return self._tracks[0].source
        except IndexError:
            return Source.UNKNOWN
