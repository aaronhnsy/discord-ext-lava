# Standard Library
from collections.abc import Callable
from typing import Literal, TypedDict

# Libraries
import discord
import spotipy


type JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
type JSONDumps = Callable[[JSON], str]
type JSONLoads = Callable[..., JSON]

type VoiceChannel = discord.VoiceChannel | discord.StageChannel

type SpotifySearchType = Literal["album", "playlist", "artist", "track"]
type SpotifySource = spotipy.Album | spotipy.Playlist | spotipy.Artist | spotipy.Track


class PlayerStateData(TypedDict):
    time: int
    position: int
    connected: bool
    ping: int


class ExceptionData(TypedDict):
    message: str | None
    severity: Literal["common", "suspicious", "fatal"]
    cause: str
