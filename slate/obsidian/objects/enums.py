# Future
from __future__ import annotations

# Standard Library
from enum import Enum


__all__ = (
    "Op",
    "LoadType",
    "QueueLoopMode",
    "Source",
    "SearchType",
    "ErrorSeverity",
    "EventType",
    "TrackEndReason",
)


class Op(Enum):
    SUBMIT_VOICE_UPDATE = 0
    STATS = 1

    SETUP_RESUMING = 2
    SETUP_DISPATCH_BUFFER = 3

    PLAYER_EVENT = 4
    PLAYER_UPDATE = 5

    PLAY_TRACK = 6
    STOP_TRACK = 7

    PLAYER_PAUSE = 8
    PLAYER_FILTERS = 9
    PLAYER_SEEK = 10
    PLAYER_DESTROY = 11
    PLAYER_CONFIGURE = 12


class LoadType(Enum):
    FAILED = "FAILED"
    NONE = "NONE"
    TRACK = "TRACK"
    TRACK_COLLECTION = "TRACK_COLLECTION"


class Source(Enum):
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    YARN = "yarn"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    NICO = "nico"
    SOUNDCLOUD = "soundcloud"
    LOCAL = "local"
    HTTP = "http"
    SPOTIFY = "spotify"
    NONE = ""


class SearchType(Enum):
    TRACK = "track"
    PLAYLIST = "playlist"
    ALBUM = "album"
    ARTIST = "artist"


class ErrorSeverity(Enum):
    COMMON = "COMMON"
    SUSPICIOUS = "SUSPICIOUS"
    FAULT = "FAULT"


class EventType(Enum):
    TRACK_START = "TRACK_START"
    TRACK_END = "TRACK_END"
    TRACK_STUCK = "TRACK_STUCK"
    TRACK_EXCEPTION = "TRACK_EXCEPTION"
    WEBSOCKET_OPEN = "WEBSOCKET_OPEN"
    WEBSOCKET_CLOSED = "WEBSOCKET_CLOSED"


class TrackEndReason(Enum):
    STOPPED = "STOPPED"
    REPLACED = "REPLACED"
    CLEANUP = "CLEANUP"
    LOAD_FAILED = "LOAD_FAILED"
    FINISHED = "FINISHED"
