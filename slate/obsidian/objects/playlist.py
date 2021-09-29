# Future
from __future__ import annotations

# Standard Library
from typing import Any, Generic, TypeVar

# Packages
import discord
from discord.ext import commands

# My stuff
from slate.objects.enums import Source
from slate.obsidian.objects.track import Track


__all__ = (
    "Playlist",
)


ContextT = TypeVar("ContextT", bound=commands.Context)


class Playlist(Generic[ContextT]):

    def __init__(
        self,
        *,
        info: dict[str, Any],
        tracks: list[dict[str, Any]],
        ctx: ContextT | None = None
    ) -> None:

        self._tracks: list[Track[ContextT]] = [Track(id=track["track"], info=track["info"], ctx=ctx) for track in tracks]
        self._ctx: ContextT | None = ctx

        self._requester: discord.Member | discord.User | None = ctx.author if (ctx and ctx.author) else None

        self._name: str = info["name"]
        self._selected_track: int = info["selected_track"]

        self._uri: str | None = info.get("uri")

    def __repr__(self) -> str:
        return f"<slate.obsidian.Playlist>"

    #

    @property
    def tracks(self) -> list[Track[ContextT]]:
        return self._tracks

    @property
    def ctx(self) -> ContextT | None:
        return self._ctx

    #

    @property
    def name(self) -> str:
        return self._name

    @property
    def selected_track(self) -> Track[ContextT] | None:

        try:
            return self._tracks[self._selected_track]
        except IndexError:
            return None

    @property
    def uri(self) -> str | None:
        return self._uri

    #

    @property
    def requester(self) -> discord.Member | discord.User | None:
        return self._requester

    #

    @property
    def source(self) -> Source:
        try:
            return self.tracks[0].source
        except KeyError:
            return Source.YOUTUBE  # Playlists *should* only be youtube sourced anyway.
