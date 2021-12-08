# Future
from __future__ import annotations

# Standard Library
from typing import Generic, TypeVar

# Packages
import spotipy
from discord.ext import commands

# My stuff
from slate.obsidian.objects.collection import Collection
from slate.obsidian.objects.enums import SearchType, Source
from slate.obsidian.objects.track import Track


__all__ = (
    "Result",
)


ContextT = TypeVar("ContextT", bound=commands.Context)


class Result(Generic[ContextT]):

    def __init__(
        self,
        *,
        search_source: Source,
        search_type: SearchType,
        search_result: spotipy.Playlist | spotipy.Album | spotipy.Artist | spotipy.Track | list[Track[ContextT]] | Collection[ContextT],
        tracks: list[Track[ContextT]]
    ) -> None:

        self._search_source: Source = search_source
        self._search_type: SearchType = search_type
        self._search_result: spotipy.Playlist | spotipy.Album | spotipy.Artist | spotipy.Track | list[Track[ContextT]] | Collection[ContextT] = search_result
        self._tracks: list[Track[ContextT]] = tracks

    def __repr__(self) -> str:
        return "<slate.obsidian.Result>"

    #

    @property
    def search_source(self) -> Source:
        return self._search_source

    @property
    def search_type(self) -> SearchType:
        return self._search_type

    @property
    def result(self) -> spotipy.Playlist | spotipy.Album | spotipy.Artist | spotipy.Track | list[Track[ContextT]] | Collection[ContextT]:
        return self._search_result

    @property
    def tracks(self) -> list[Track[ContextT]]:
        return self._tracks
