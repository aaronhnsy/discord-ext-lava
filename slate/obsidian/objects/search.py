# Future
from __future__ import annotations

# Standard Library
from typing import Generic, TypeVar

# Packages
import aiospotify
from discord.ext import commands

# My stuff
from slate.objects.enums import SearchType, Source
from slate.obsidian.objects.playlist import Playlist
from slate.obsidian.objects.track import Track


__all__ = (
    "SearchResult",
)


ContextT = TypeVar("ContextT", bound=commands.Context)


class SearchResult(Generic[ContextT]):

    def __init__(
        self,
        source: Source,
        type: SearchType,
        result: aiospotify.Playlist | aiospotify.Album | aiospotify.Artist | aiospotify.Track | list[Track[ContextT]] | Playlist[ContextT],
        tracks: list[Track[ContextT]]
    ) -> None:

        self._source: Source = source
        self._type: SearchType = type
        self._result = result
        self._tracks = tracks

    def __repr__(self) -> str:
        return f"<slate.obsidian.SearchResult>"

    #

    @property
    def source(self) -> Source:
        return self._source

    @property
    def type(self) -> SearchType:
        return self._type

    @property
    def result(self) -> aiospotify.Playlist | aiospotify.Album | aiospotify.Artist | aiospotify.Track | list[Track[ContextT]] | Playlist[ContextT]:
        return self._result

    @property
    def tracks(self) -> list[Track[ContextT]]:
        return self._tracks
