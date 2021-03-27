from __future__ import annotations

from typing import Dict, List, Optional, Protocol

from discord.ext import commands

from slate.objects.track import Track


class Playlist:
    """
    A class representing a Playlist object sent from :resource:`lavalink <lavalink>` or :resource:`andesite <andesite>` (or another provider).

    Parameters
    ----------
    playlist_info : dict
        Information about the playlist.
    tracks : List [dict]
        A list of dictionaries containing track information.
    ctx : Optional [ :py:class:`commands.Context` ]
        An optional discord.py context object that allows for quality of life attributes such as :py:attr:`Track.requester`.


    .. note::
        This class uses :ref:`py:slots` which means you can't use dynamic attributes.
    """

    __slots__ = '_playlist_info', '_raw_tracks', '_ctx', '_tracks', '_name', '_selected_track'

    def __init__(self, *, playlist_info: dict, tracks: List[Dict], ctx: Protocol[commands.Context] = None) -> None:

        self._playlist_info = playlist_info
        self._raw_tracks = tracks
        self._ctx = ctx

        self._tracks = [Track(track_id=track.get('track'), track_info=track.get('info'), ctx=ctx) for track in self._raw_tracks]

        self._name = self._playlist_info.get('name')
        self._selected_track = self._playlist_info.get('selectedTrack')

    def __repr__(self) -> str:
        return f'<slate.Playlist name=\'{self._name}\' selected_track={self.selected_track} track_count={len(self._tracks)}>'

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

    @property
    def tracks(self) -> List[Track]:
        """
        List [ :py:class:`Track` ]:
            A list of Track objects that this playlist has.
        """
        return self._tracks
