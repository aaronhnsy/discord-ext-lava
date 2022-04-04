# Future
from __future__ import annotations

# Standard Library
from enum import Enum


__all__ = (
    "Provider",
    "QueueLoopMode",
    "Source",
)


class Provider(Enum):
    OBSIDIAN = 0
    LAVALINK = 1


class QueueLoopMode(Enum):
    DISABLED = 0
    ALL = 1
    CURRENT = 2


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
    UNKNOWN = "unknown"
    NONE = ""
