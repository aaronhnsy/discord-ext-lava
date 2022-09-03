from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

import discord
import spotipy
from discord.ext import commands


if TYPE_CHECKING:
    from .objects.track import Track
    from .player import Player


__all__ = (
    "JSONDumps",
    "JSONLoads",
    "VoiceChannel",
    "SpotifySearchTrack",
    "SpotifySearchResult",
    "BotT",
    "PlayerT",
    "QueueItemT"
)


JSONDumps = Callable[..., str]
JSONLoads = Callable[..., dict[str, Any]]

VoiceChannel = discord.VoiceChannel | discord.StageChannel

SpotifySearchTrack = spotipy.SimpleTrack | spotipy.Track | spotipy.PlaylistTrack
SpotifySearchResult = spotipy.Album | spotipy.Playlist | spotipy.Artist | spotipy.Track

BotT = TypeVar("BotT", bound=commands.Bot | commands.AutoShardedBot)
PlayerT = TypeVar("PlayerT", bound="Player[Any, Any]")
QueueItemT = TypeVar("QueueItemT", bound="Track")
