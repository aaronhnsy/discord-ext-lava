from __future__ import annotations

from typing import Any, Generic, List, Optional, TypeVar, Union

import discord
from discord.ext import commands

from .enums import TrackSource
from .track import ObsidianTrack


ContextType = TypeVar('ContextType', bound=commands.Context)


__all__ = ['ObsidianPlaylist']


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
    def uri(self):
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
