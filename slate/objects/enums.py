# Future
from __future__ import annotations

# Standard Library
from enum import Enum


__all__ = (
    "QueueLoopMode",
    "ErrorSeverity",
    "SearchType",
    "Source"
)


class QueueLoopMode(Enum):
    OFF = 0
    NONE = OFF

    CURRENT = 1
    QUEUE = 2


class ErrorSeverity(Enum):
    COMMON = "COMMON"
    SUSPICIOUS = "SUSPICIOUS"
    FAULT = "FAULT"


class SearchType(Enum):

    # Obsidian types
    SEARCH_RESULT = "searchresult"
    PLAYLIST = "playlist"
    ALBUM = "album"

    # Custom types
    TRACK = "track"
    ARTIST = "artist"


class Source(Enum):

    # Obsidian sources
    BANDCAMP = "bandcamp"
    YARN = "getyarn.io"
    HTTP = "http"
    LOCAL = "local"
    NICO = "niconico"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    YOUTUBE = "youtube"

    # Custom sources
    YOUTUBE_MUSIC = "youtube_music"
    SPOTIFY = "spotify"
    NONE = ""
