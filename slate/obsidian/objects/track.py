# Future
from __future__ import annotations

# Standard Library
from typing import Any, Generic, TypeVar

# Packages
import discord
from discord.ext import commands

# My stuff
from slate.obsidian.objects.enums import Source


__all__ = (
    "Track",
)


ContextT = TypeVar("ContextT", bound=commands.Context)


class Track(Generic[ContextT]):

    def __init__(
        self,
        *,
        id: str,
        info: dict[str, Any],
        ctx: ContextT | None = None
    ) -> None:

        self._id: str = id
        self._ctx: ContextT | None = ctx

        self._requester: discord.Member | discord.User | None = ctx.author if (ctx and ctx.author) else None

        self._title: str = info["title"]
        self._author: str = info["author"]
        self._uri: str = info["uri"]
        self._identifier: str = info["identifier"]
        self._length: int = info["length"]
        self._position: int = info["position"]
        self._is_stream: bool = info["is_stream"]
        self._is_seekable: bool = info["is_seekable"]
        self._source: Source = Source(info["source_name"])

        self._thumbnail: str | None = info.get("thumbnail")

    def __repr__(self) -> str:
        return "<slate.obsidian.Track>"

    #

    @property
    def id(self) -> str:
        return self._id

    @property
    def ctx(self) -> ContextT | None:
        return self._ctx

    #

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def length(self) -> int:
        return self._length

    @property
    def position(self) -> int:
        return self._position

    def is_stream(self) -> bool:
        return self._is_stream

    def is_seekable(self) -> bool:
        return self._is_seekable

    @property
    def source(self) -> Source:
        return self._source

    #

    @property
    def thumbnail(self) -> str:

        if self.source is Source.YOUTUBE:
            return f"https://img.youtube.com/vi/{self.identifier}/hqdefault.jpg"

        if self._thumbnail:
            return self._thumbnail

        return "https://dummyimage.com/1920x1080/000/fff.png&text=+"

    @property
    def requester(self) -> discord.Member | discord.User | None:
        return self._requester
