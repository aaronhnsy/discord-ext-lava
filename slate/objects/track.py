# Future
from __future__ import annotations

# Standard Library
from typing import Any, Generic, TypeVar

# Packages
import discord
from discord.ext import commands

# My stuff
from .enums import Source


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
        self._source: Source = Source(info.get("source_name", info.get("sourceName", "Unknown")))
        self._artwork_url: str | None = info.get("artwork_url")
        self._isrc: str | None = info.get("isrc")

        self._is_stream: bool = info.get("is_stream", info.get("isStream", False))
        self._is_seekable: bool = info.get("is_seekable", info.get("isSeekable", False))

    def __repr__(self) -> str:
        return f"<slate.Track title='{self.title}', author='{self.author}'>"

    #

    @property
    def id(self) -> str:
        return self._id

    @property
    def ctx(self) -> ContextT | None:
        return self._ctx

    @property
    def requester(self) -> discord.Member | discord.User | None:
        return self._requester

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

    @property
    def source(self) -> Source:
        return self._source

    @property
    def artwork_url(self) -> str | None:

        if self._artwork_url:
            return self._artwork_url
        elif self.source is Source.YOUTUBE:
            return f"https://img.youtube.com/vi/{self.identifier}/hqdefault.jpg"

        return "https://dummyimage.com/1920x1080/000/fff.png&text=+"

    @property
    def isrc(self) -> str | None:
        return self._isrc

    # Utilities

    def is_stream(self) -> bool:
        return self._is_stream

    def is_seekable(self) -> bool:
        return self._is_seekable
