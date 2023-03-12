from collections.abc import Callable
from typing import Literal, TypeAlias, TypedDict

import discord
import spotipy


JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

JSONDumps: TypeAlias = Callable[[JSON], str]
JSONLoads: TypeAlias = Callable[..., JSON]

VoiceChannel: TypeAlias = discord.VoiceChannel | discord.StageChannel

SpotifySearchType: TypeAlias = Literal["album", "playlist", "artist", "track"]
SpotifySource: TypeAlias = spotipy.Album | spotipy.Playlist | spotipy.Artist | spotipy.Track


class ExceptionData(TypedDict):
    message: str | None
    severity: Literal["COMMON", "SUSPICIOUS", "FATAL"]
    cause: str
