from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar

from discord import Member
from discord.ext.commands import Context

from .track import ObsidianTrack
from ...objects.enums import Source


__all__ = ["ObsidianPlaylist"]

ContextType = TypeVar("ContextType", bound=Context)


class ObsidianPlaylist(Generic[ContextType]):

    def __init__(
        self,
        *,
        info: dict[str, Any],
        tracks: list[dict[str, Any]],
        ctx: Optional[ContextType] = None
    ) -> None:

        self._tracks: list[ObsidianTrack[ContextType]] = [ObsidianTrack(id=track["track"], info=track["info"], ctx=ctx) for track in tracks]
        self._ctx: Optional[ContextType] = ctx

        self._requester: Optional[Member] = ctx.author if ctx else None

        self._name: str = info["name"]
        self._selected_track: int = info["selected_track"]

        self._uri: Optional[str] = info.get("uri")

    def __repr__(self) -> str:
        return f"<slate.ObsidianPlaylist name='{self._name}' selected_track={self.selected_track} track_count={len(self._tracks)}>"

    #

    @property
    def tracks(self) -> list[ObsidianTrack[ContextType]]:
        return self._tracks

    @property
    def ctx(self) -> Optional[ContextType]:
        return self._ctx

    #

    @property
    def name(self) -> str:
        return self._name

    @property
    def selected_track(self) -> Optional[ObsidianTrack[ContextType]]:

        try:
            return self._tracks[self._selected_track]
        except IndexError:
            return None

    @property
    def uri(self) -> Optional[str]:
        return self._uri

    #

    @property
    def requester(self) -> Optional[Member]:
        return self._requester

    #

    @property
    def source(self) -> Source:
        try:
            return self.tracks[0].source
        except KeyError:
            return Source.YOUTUBE  # Playlists *should* only be youtube sourced anyway.
