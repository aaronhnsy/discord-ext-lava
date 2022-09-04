from __future__ import annotations

from enum import Enum


__all__ = (
    "Provider",
    "QueueLoopMode",
    "Source",
)


class Provider(Enum):
    Obsidian = 0
    Lavalink = 1


class QueueLoopMode(Enum):
    Disabled = 0
    All = 1
    Current = 2


class Source(Enum):
    Bandcamp = "bandcamp"
    GetYarn = "getyarn.io"
    Http = "http"
    Local = "local"
    NicoNico = "niconico"
    SoundCloud = "soundcloud"
    Twitch = "twitch"
    Vimeo = "vimeo"
    Youtube = "youtube"
    YoutubeMusic = "youtube_music"
    Spotify = "spotify"
    Unknown = "unknown"
    NONE = ""
