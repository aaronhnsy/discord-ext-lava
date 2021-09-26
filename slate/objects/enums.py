# Future
from __future__ import annotations

# Standard Library
from enum import Enum


__all__ = ['QueueLoopMode', 'Source', 'SearchType', 'ErrorSeverity', 'LoadType', 'EventType', 'TrackEndReason']


class QueueLoopMode(Enum):
    OFF = 0
    NONE = OFF

    CURRENT = 1
    QUEUE = 2


class Source(Enum):
    YOUTUBE = 'youtube'
    YOUTUBE_MUSIC = 'youtube_music'
    YARN = 'yarn'
    BANDCAMP = 'bandcamp'
    TWITCH = 'twitch'
    VIMEO = 'vimeo'
    NICO = 'nico'
    SOUNDCLOUD = 'soundcloud'
    LOCAL = 'local'
    HTTP = 'http'
    SPOTIFY = 'spotify'


class SearchType(Enum):
    TRACK = 'track'
    PLAYLIST = 'playlist'
    ALBUM = 'album'
    ARTIST = 'artist'


class ErrorSeverity(Enum):
    COMMON = 'COMMON'
    SUSPICIOUS = 'SUSPICIOUS'
    FAULT = 'FAULT'


class LoadType(Enum):
    NO_MATCHES = 'NO_MATCHES'
    LOAD_FAILED = 'LOAD_FAILED'
    PLAYLIST_LOADED = 'PLAYLIST_LOADED'
    TRACK_LOADED = 'TRACK_LOADED'
    SEARCH_RESULT = 'SEARCH_RESULT'


class EventType(Enum):
    TRACK_START = 'TRACK_START'
    TRACK_END = 'TRACK_END'
    TRACK_STUCK = 'TRACK_STUCK'
    TRACK_EXCEPTION = 'TRACK_EXCEPTION'
    WEBSOCKET_OPEN = 'WEBSOCKET_OPEN'
    WEBSOCKET_CLOSED = 'WEBSOCKET_CLOSED'


class TrackEndReason(Enum):
    STOPPED = 'STOPPED'
    REPLACED = 'REPLACED'
    CLEANUP = 'CLEANUP'
    LOAD_FAILED = 'LOAD_FAILED'
    FINISHED = 'FINISHED'
