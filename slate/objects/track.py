from __future__ import annotations

from typing import Optional, Protocol, Union

import discord
from discord.ext import commands


class Track:

    __slots__ = '_track_id', '_track_info', '_ctx', '_class', '_title', '_author', '_length', '_identifier', '_uri', '_is_stream', '_is_seekable', '_position', '_requester'

    def __init__(self, *, track_id: str, track_info: dict, ctx: Protocol[commands.Context] = None) -> None:

        self._track_id = track_id
        self._track_info = track_info
        self._ctx = ctx

        self._class = track_info.get('class', 'UNKNOWN')

        self._title = track_info.get('title')
        self._author = track_info.get('author')
        self._length = track_info.get('length')
        self._identifier = track_info.get('identifier')
        self._uri = track_info.get('uri')
        self._is_stream = track_info.get('isStream')
        self._is_seekable = track_info.get('isSeekable')
        self._position = track_info.get('position')

        self._requester = None
        if ctx:
            self._requester = ctx.author

    def __repr__(self) -> str:
        return f'<slate.Track title=\'{self._title}\' uri=\'<{self._uri}>\' source=\'{self.source}\' length={self._length}>'

    #

    @property
    def track_id(self) -> str:
        return self._track_id

    @property
    def ctx(self) -> Optional[Protocol[commands.Context]]:
        return self._ctx

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    @property
    def length(self) -> int:
        return self._length

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def is_stream(self) -> bool:
        return self._is_stream

    @property
    def is_seekable(self) -> bool:
        return self._is_seekable

    @property
    def position(self) -> int:
        return self._position

    @property
    def requester(self) -> Optional[Union[discord.Member, discord.User]]:
        return self._requester

    #

    @property
    def source(self) -> str:

        if not self.uri:
            return 'UNKNOWN'

        for source in ['bandcamp', 'beam', 'soundcloud', 'twitch', 'vimeo', 'youtube', 'spotify']:
            if source in self.uri:
                return source.title()

        return 'HTTP'

    @property
    def thumbnail(self) -> str:

        if self.source == 'Youtube':
            return f'https://img.youtube.com/vi/{self.identifier}/mqdefault.jpg'

        if (thumbnail := self._track_info.get('thumbnail', None)) is not None:
            return thumbnail

        return f'https://dummyimage.com/1280x720/000/fff.png&text=+'
