# Future
from __future__ import annotations

# Standard Library
from typing import Any, Generic

# Packages
import discord

# Local
from ..types import ContextT
from .enums import Source
from .track import Track


__all__ = (
    "Collection",
)


class Collection(Generic[ContextT]):

    def __init__(
        self,
        *,
        info: dict[str, Any],
        tracks: list[dict[str, Any]],
        ctx: ContextT | None = None
    ) -> None:

        self._name: str = info["name"]
        self._url: str = info["url"]
        self._selected_track: int | None = info.get("selected_track") or info.get("selectedTrack")

        self._tracks: list[Track[ContextT]] = [Track(id=track["track"], info=track["info"], ctx=ctx) for track in tracks]

        self._ctx: ContextT | None = ctx
        self._requester: discord.Member | discord.User | None = ctx.author if (ctx and ctx.author) else None

    def __repr__(self) -> str:
        return "<slate.Collection>"

    # Properties

    @property
    def name(self) -> str:
        return self._name

    @property
    def url(self) -> str:
        return self._url

    @property
    def selected_track(self) -> Track[ContextT] | int | None:

        if not self._selected_track:
            return None

        try:
            return self._tracks[self._selected_track]
        except IndexError:
            return self._selected_track

    @property
    def tracks(self) -> list[Track[ContextT]]:
        return self._tracks

    @property
    def ctx(self) -> ContextT | None:
        return self._ctx

    @property
    def requester(self) -> discord.Member | discord.User | None:
        return self._requester

    @property
    def source(self) -> Source:

        try:
            return self._tracks[0].source
        except IndexError:
            return Source.UNKNOWN
