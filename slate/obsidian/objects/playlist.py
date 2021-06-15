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

from typing import Any, Generic, List, Optional, TypeVar, Union

import discord
from discord.ext import commands

from .enums import TrackSource
from .track import ObsidianTrack


__all__ = ['ObsidianPlaylist']


ContextType = TypeVar('ContextType', bound=commands.Context)


class ObsidianPlaylist(Generic[ContextType]):

    __slots__ = '_tracks', '_ctx', '_requester', '_name', '_selected_track', '_uri'

    def __init__(self, *, info: dict[str, Any], tracks: List[dict[str, Any]], ctx: Optional[ContextType] = None) -> None:

        self._tracks: List[ObsidianTrack[ContextType]] = [ObsidianTrack(id=track['track'], info=track['info'], ctx=ctx) for track in tracks]
        self._ctx: Optional[ContextType] = ctx

        self._requester: Optional[Union[discord.User, discord.Member]] = ctx.author if ctx else None

        self._name: str = info['name']
        self._selected_track: int = info['selected_track']

        self._uri: Optional[str] = info.get('uri')

    def __repr__(self) -> str:
        return f'<slate.ObsidianPlaylist name=\'{self._name}\' selected_track={self.selected_track} track_count={len(self._tracks)}>'

    #

    @property
    def tracks(self) -> List[ObsidianTrack[ContextType]]:
        return self._tracks

    @property
    def ctx(self) -> Optional[ContextType]:
        return self._ctx

    #

    @property
    def name(self) -> str:
        return self._name

    @property
    def selected_track(self) -> Optional[ObsidianTrack[ContextType]]:

        try:
            return self._tracks[self._selected_track]
        except IndexError:
            return None

    @property
    def uri(self) -> Optional[str]:
        return self._uri

    #

    @property
    def requester(self) -> Optional[Union[discord.Member, discord.User]]:
        return self._requester

    #

    @property
    def source(self) -> TrackSource:
        try:
            return self.tracks[0].source
        except KeyError:
            return TrackSource.YOUTUBE  # Playlists *should* only be youtube sourced anyway.
