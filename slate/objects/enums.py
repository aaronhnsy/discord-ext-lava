# Future
from __future__ import annotations

# Standard Library
from enum import Enum


__all__ = (
    "NodeType",
    "QueueLoopMode",
    "Source",
    "SearchType",
)


class NodeType(Enum):
    OBSIDIAN = 0
    LAVALINK = 1


class QueueLoopMode(Enum):
    OFF = 0
    CURRENT = 1
    QUEUE = 2


class Source(Enum):

    BANDCAMP = "bandcamp"
    YARN = "getyarn.io"
    HTTP = "http"
    LOCAL = "local"
    NICO = "niconico"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    SPOTIFY = "spotify"
    NONE = ""


class SearchType(Enum):

    SEARCH_RESULT = "searchresult"
    PLAYLIST = "playlist"
    ALBUM = "album"
    TRACK = "track"
    ARTIST = "artist"
