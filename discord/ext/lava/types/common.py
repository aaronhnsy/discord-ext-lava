from collections.abc import Callable
from typing import Literal, TypedDict

import spotipy


type JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
type JSONDumps = Callable[[JSON], str]
type JSONLoads = Callable[..., JSON]

type SpotifySearchType = Literal["album", "playlist", "artist", "track"]
type SpotifySource = spotipy.Album | spotipy.Playlist | spotipy.Artist | spotipy.Track


class PlayerStateData(TypedDict):
    connected: bool
    ping: int
    time: int
    position: int


class ExceptionData(TypedDict):
    message: str | None
    severity: Literal["common", "suspicious", "fatal"]
    cause: str
