from collections.abc import Callable
from typing import TypeAlias

import discord
import spotipy


JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

JSONDumps: TypeAlias = Callable[[JSON], str]
JSONLoads: TypeAlias = Callable[..., JSON]

VoiceChannel: TypeAlias = discord.VoiceChannel | discord.StageChannel

SpotifyTrack: TypeAlias = spotipy.SimpleTrack | spotipy.Track | spotipy.PlaylistTrack
SpotifyResult: TypeAlias = spotipy.Album | spotipy.Playlist | spotipy.Artist | spotipy.Track