# Future
from __future__ import annotations

# Standard Library
from typing import Any, Generic, Optional, TypeVar

# Packages
from discord import Member
from discord.ext.commands import Context

# My stuff
from ...objects.enums import Source


__all__ = ["ObsidianTrack"]

ContextType = TypeVar("ContextType", bound=Context)


class ObsidianTrack(Generic[ContextType]):

    def __init__(
        self,
        *,
        id: str,
        info: dict[str, Any],
        ctx: Optional[ContextType] = None
    ) -> None:

        self._id: str = id
        self._ctx: Optional[ContextType] = ctx

        self._requester: Optional[Member] = ctx.author if ctx else None

        self._title: str = info["title"]
        self._author: str = info["author"]
        self._uri: str = info["uri"]
        self._identifier: str = info["identifier"]
        self._length: int = info["length"]
        self._position: int = info["position"]
        self._is_stream: bool = info["is_stream"]
        self._is_seekable: bool = info["is_seekable"]
        self._source: Source = Source(info["source_name"])

        self._thumbnail: Optional[str] = info.get("thumbnail")

    def __repr__(self) -> str:
        return f"<slate.ObsidianTrack title='{self._title}' uri='<{self._uri}>' source='{self.source}' length={self._length}>"

    #

    @property
    def id(self) -> str:
        return self._id

    @property
    def ctx(self) -> Optional[ContextType]:
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
    def requester(self) -> Optional[Member]:
        return self._requester
