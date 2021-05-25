from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Union

import discord
from discord.ext import commands


if TYPE_CHECKING:
    from slate import ContextType


__all__ = ['Track']


class Track:
    """
    A class representing a Track object sent from :resource:`lavalink <lavalink>` or :resource:`andesite <andesite>`.

    Parameters
    ----------
    track_id : str
        The Base64 encoded track data that serves as it's unique id.
    track_info : dict
        Information about the track.
    ctx : Optional [ :py:class:`commands.Context` ]
        An optional discord.py context object that allows for quality of life attributes such as :py:attr:`Track.requester`.


    .. note::
        This class uses :ref:`py:slots` which means you can't add dynamic attributes.
    """

    __slots__ = '_track_id', '_track_info', '_ctx', '_class', '_title', '_author', '_length', '_identifier', '_uri', '_is_stream', '_is_seekable', '_position', '_requester', '_source_name'

    def __init__(self, *, track_id: str, track_info: dict, ctx: ContextType = None) -> None:

        self._track_id: str = track_id
        self._ctx: ContextType = ctx

        self._requester: Optional[Union[discord.User, discord.Member]] = ctx.author if ctx else None

        self._title: str = track_info.get('title')
        self._author: str = track_info.get('author')
        self._length: int = track_info.get('length')
        self._identifier: str = track_info.get('identifier')
        self._uri: str = track_info.get('uri')
        self._is_stream: bool = track_info.get('isStream')
        self._is_seekable: bool = track_info.get('isSeekable')
        self._position: int = track_info.get('position')
        self._source_name: str = track_info.get('sourceName')

    def __repr__(self) -> str:
        return f'<slate.Track title=\'{self._title}\' uri=\'<{self._uri}>\' source=\'{self.source}\' length={self._length}>'

    #

    @property
    def track_id(self) -> str:
        """
        :py:class:`str` :
            The Base64 encoded track data that serves as this it's unique id.
        """
        return self._track_id

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
    def title(self) -> str:
        """
        :py:class:`str` :
            The title of the track.
        """
        return self._title

    @property
    def author(self) -> str:
        """
        :py:class:`str`:
            The author of the track.
        """
        return self._author

    @property
    def length(self) -> int:
        """
        :py:class:`int` :
            The length of the track in milliseconds.
        """
        return self._length

    @property
    def identifier(self) -> str:
        """
        :py:class:`str` :
            The tracks identifier, on youtube this is the videos id.
        """
        return self._identifier

    @property
    def uri(self) -> str:
        """
        :py:class:`str` :
            The URL of the track.
        """
        return self._uri

    @property
    def is_stream(self) -> bool:
        """
        :py:class:`bool` :
            Whether or not the track is a stream.
        """
        return self._is_stream

    @property
    def is_seekable(self) -> bool:
        """
        :py:class:`bool` :
            Whether or not the track is seekable.
        """
        return self._is_seekable

    @property
    def position(self) -> int:
        """
        :py:class:`int` :
            The current position of the track in milliseconds.
        """
        return self._position

    @property
    def source(self) -> str:
        """
        :py:class:`str` :
            The source of the track. (Youtube, HTTP, Twitch, Soundcloud, etc)
        """

        if self._source_name:
            return self._source_name

        if not self.uri:
            return 'UNKNOWN'

        for source in ['bandcamp', 'beam', 'soundcloud', 'twitch', 'vimeo', 'youtube', 'spotify']:
            if source in self.uri:
                return source.title()

        return 'HTTP'

    #

    @property
    def thumbnail(self) -> str:
        """
        :py:class:`str` :
            The thumbnail of the track. Returns a dummy 1280x720 image if not found.
        """

        if self.source == 'Youtube':
            return f'https://img.youtube.com/vi/{self.identifier}/mqdefault.jpg'

        if (thumbnail := self._track_info.get('thumbnail', None)) is not None:
            return thumbnail

        return 'https://dummyimage.com/1920x1080/000/fff.png&text=+'
