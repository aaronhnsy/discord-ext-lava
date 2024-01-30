# Standard Library
from typing import Any, TypedDict


class TrackInfoData(TypedDict):
    identifier: str
    isSeekable: bool
    author: str
    length: int
    isStream: bool
    position: int
    title: str
    uri: str | None
    artworkUrl: str | None
    isrc: str | None
    sourceName: str


type TrackPluginInfoData = dict[str, Any]
type TrackUserData = dict[str, Any]


class TrackData(TypedDict):
    encoded: str
    info: TrackInfoData
    pluginInfo: TrackPluginInfoData
    userData: TrackUserData
