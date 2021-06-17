"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from typing import Generic, TYPE_CHECKING, TypeVar, Union

from spotify import Album, Artist, Playlist, Track

from .enums import SearchType, Source


if TYPE_CHECKING:

    from typing import Any

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
