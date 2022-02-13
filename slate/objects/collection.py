# Future
from __future__ import annotations

# Standard Library
from typing import Any, Generic, TypeVar

# Packages
import discord
from discord.ext import commands

# My stuff
from .enums import SearchType, Source
from .track import Track


__all__ = (
    "Collection",
)


ContextT = TypeVar("ContextT", bound=commands.Context)


class Collection(Generic[ContextT]):

    def __init__(
        self,
        *,
        info: dict[str, Any],
        tracks: list[dict[str, Any]],
        ctx: ContextT | None = None
    ) -> None:

        self._name: str = info["name"]
        self._url: str | None = info["url"]
        self._selected_track: int | None = info["selected_track"]
        self._search_type: SearchType = SearchType(info["type"]["name"].lower())

        self._tracks: list[Track[ContextT]] = [Track(id=track["track"], info=track["info"], ctx=ctx) for track in tracks]
        self._ctx: ContextT | None = ctx

        self._requester: discord.Member | discord.User | None = ctx.author if (ctx and ctx.author) else None

    def __repr__(self) -> str:
        return "<slate.obsidian.Collection>"

    #

    @property
    def name(self) -> str:
        return self._name

    @property
    def url(self) -> str | None:
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
    def search_type(self) -> SearchType:
        return self._search_type

    @property
    def source(self) -> Source:

        try:
            return self.tracks[0].source
        except KeyError:
            return Source.NONE

    #

    @property
    def tracks(self) -> list[Track[ContextT]]:
        return self._tracks

    @property
    def ctx(self) -> ContextT | None:
        return self._ctx

    #

    @property
    def requester(self) -> discord.Member | discord.User | None:
        return self._requester
