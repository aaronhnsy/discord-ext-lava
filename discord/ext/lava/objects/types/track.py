from typing import TypedDict


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


class TrackData(TypedDict):
    encoded: str
    info: TrackInfoData
