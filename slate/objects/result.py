# Future
from __future__ import annotations

# Standard Library
from typing import Generic, TypeVar

# Packages
import spotipy
from discord.ext import commands

# My stuff
from .collection import Collection
from .enums import Source
from .track import Track


__all__ = (
    "Result",
)


ContextT = TypeVar("ContextT", bound=commands.Context)


class Result(Generic[ContextT]):

    def __init__(
        self,
        *,
        source: Source,
        type: str,
        result: spotipy.Playlist | spotipy.Album | spotipy.Artist | spotipy.Track | Track[ContextT] | list[Track[ContextT]] | Collection[ContextT],
        tracks: list[Track[ContextT]]
    ) -> None:

        self._source: Source = source
        self._type: str = type
        self._result: spotipy.Playlist | spotipy.Album | spotipy.Artist | spotipy.Track | Track[ContextT] | list[Track[ContextT]] | Collection[ContextT] = result
        self._tracks: list[Track[ContextT]] = tracks

    def __repr__(self) -> str:
        return "<slate.Result>"

    #

    @property
    def source(self) -> Source:
        return self._source

    @property
    def type(self) -> str:
        return self._type

    @property
    def result(self) -> spotipy.Playlist | spotipy.Album | spotipy.Artist | spotipy.Track | Track[ContextT] | list[Track[ContextT]] | Collection[ContextT]:
        return self._result

    @property
    def tracks(self) -> list[Track[ContextT]]:
        return self._tracks
