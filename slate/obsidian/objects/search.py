# Future
from __future__ import annotations

# Standard Library
from typing import Generic, TypeVar

# Packages
from aiospotify import Album, Artist, Playlist, Track
from discord.ext import commands

# My stuff
from slate.objects.enums import SearchType, Source
from slate.obsidian.objects.playlist import ObsidianPlaylist
from slate.obsidian.objects.track import ObsidianTrack


__all__ = (
    "SearchResult",
)


ContextT = TypeVar("ContextT", bound=commands.Context)


class SearchResult(Generic[ContextT]):

    def __init__(
        self,
        source: Source,
        type: SearchType,
        result: Playlist | Album | Artist | Track | list[ObsidianTrack[ContextT]] | ObsidianPlaylist[ContextT],
        tracks: list[ObsidianTrack[ContextT]]
    ) -> None:
        self._source: Source = source
        self._type: SearchType = type
        self._result = result
        self._tracks = tracks

    def __repr__(self) -> str:
        return f"<slate.SearchResult, source={self.source!r}, type={self.type!r}, result={self.result!r}>"

    #

    @property
    def source(self) -> Source:
        return self._source

    @property
    def type(self) -> SearchType:
        return self._type

    @property
    def result(self) -> Playlist | Album | Artist | Track | list[ObsidianTrack[ContextT]] | ObsidianPlaylist[ContextT]:
        return self._result

    @property
    def tracks(self) -> list[ObsidianTrack[ContextT]]:
        return self._tracks
