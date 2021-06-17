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

from enum import Enum


__all__ = ['QueueLoopMode', 'Source', 'SearchType', 'ErrorSeverity', 'LoadType', 'EventType', 'TrackEndReason']


class QueueLoopMode(Enum):
    OFF = 0
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
