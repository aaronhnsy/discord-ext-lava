from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING, Union

import discord
from discord.ext import commands

from slate.objects.track import Track


if TYPE_CHECKING:
    from slate import ContextType


__all__ = ['Playlist']


class Playlist:
    """
    A class representing a Playlist object sent from :resource:`lavalink <lavalink>` or :resource:`andesite <andesite>` (or another provider).

    Parameters
    ----------
    playlist_info : dict
        Information about the playlist.
    tracks : :py:class:`List` [dict]
        A list of dictionaries containing track information.
    ctx : Optional [ :py:class:`commands.Context` ]
        An optional discord.py context object that allows for quality of life attributes such as :py:attr:`Track.requester`.


    .. note::
        This class uses :ref:`py:slots` which means you can't use dynamic attributes.
    """

    __slots__ = '_playlist_info', '_tracks', '_ctx', '_requester', '_name', '_selected_track'

    def __init__(self, *, playlist_info: dict, tracks: List[dict], ctx: ContextType = None) -> None:

        self._tracks: List[Track] = [Track(track_id=track.get('track'), track_info=track.get('info'), ctx=ctx) for track in tracks]
        self._ctx: ContextType = ctx

        self._requester: Optional[Union[discord.User, discord.Member]] = ctx.author if ctx else None

        self._name: str = playlist_info.get('name')
        self._selected_track: int = playlist_info.get('selectedTrack')

    def __repr__(self) -> str:
        return f'<slate.Playlist name=\'{self._name}\' selected_track={self.selected_track} track_count={len(self._tracks)}>'

    #

    @property
    def tracks(self) -> List[Track]:
        """
        :py:class:`List` [ :py:class:`Track` ]:
            A list of Track objects that this playlist has.
        """
        return self._tracks

    @property
    def ctx(self) -> Optional[ContextType]:
        """
        Optional [ :py:class:`commands.Context` ]:
            A discord.py context object that allows access to attributes such as :py:attr:`Track.requester`.
        """
        return self._ctx

    @property
    def requester(self) -> Optional[Union[discord.Member, discord.User]]:
        """
        Optional [ :py:class:`Union` [ :py:class:`discord.Member` , :py:class:`discord.User` ] ]:
            The discord user or member who requested the track. Only available if :py:attr:`Track.context` is not None.
        """
        return self._requester

    #

    @property
    def name(self) -> str:
        """
        :py:class:`str`:
            The name of this playlist.
        """
        return self._name

    @property
    def selected_track(self) -> Optional[Track]:
        """
        Optional [ :py:class:`Track` ]:
            The Track selected when this playlist was fetched, could be None.
        """

        try:
            return self._tracks[self._selected_track]
        except IndexError:
            return None
