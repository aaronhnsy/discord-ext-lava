# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Generic, TypeVar, Union

# Packages
from aiospotify import Album, Artist, Playlist, Track

# My stuff
from .enums import SearchType, Source


if TYPE_CHECKING:

    # Standard Library
    from typing import Any

    # My stuff
    from ..obsidian.objects.playlist import ObsidianPlaylist
    from ..obsidian.objects.track import ObsidianTrack

__all__ = ['SearchResult']

TrackT = TypeVar('TrackT', bound='ObsidianTrack[Any]')
PlaylistT = TypeVar('PlaylistT', bound='ObsidianPlaylist[Any]')


class SearchResult(Generic[TrackT, PlaylistT]):
    __slots__ = ['_source', '_type', '_result', '_tracks']

    def __init__(self, source: Source, type: SearchType, result: Union[Playlist, Album, Artist, Track, list[TrackT], PlaylistT], tracks: list[TrackT]) -> None:
        self._source: Source = source
        self._type: SearchType = type
        self._result = result
        self._tracks = tracks

    def __repr__(self) -> str:
        return f'<slate.SearchResult, source={self.source!r}, type={self.type!r}, result={self.result!r}>'

    #

    @property
    def source(self) -> Source:
        return self._source

    @property
    def type(self) -> SearchType:
        return self._type

    @property
    def result(self) -> Union[Playlist, Album, Artist, Track, list[TrackT], PlaylistT]:
        return self._result

    @property
    def tracks(self) -> list[TrackT]:
        return self._tracks
