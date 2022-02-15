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
    "Search",
)


ContextT = TypeVar("ContextT", bound=commands.Context)
Result = spotipy.Album | spotipy.Playlist | spotipy.Artist | spotipy.Track | list[Track[ContextT]] | Collection[ContextT]


class Search(Generic[ContextT]):

    def __init__(
        self,
        *,
        source: Source,
        type: str,
        result: Result[ContextT],
        tracks: list[Track[ContextT]]
    ) -> None:

        self._source: Source = source
        self._type: str = type
        self._result: Result[ContextT] = result
        self._tracks: list[Track[ContextT]] = tracks

    def __repr__(self) -> str:
        return f"<slate.Result source={self._source}, type='{self._type}', result={type(self._result)}>"

    # Properties

    @property
    def source(self) -> Source:
        return self._source

    @property
    def type(self) -> str:
        return self._type

    @property
    def result(self) -> Result[ContextT]:
        return self._result

    @property
    def tracks(self) -> list[Track[ContextT]]:
        return self._tracks
