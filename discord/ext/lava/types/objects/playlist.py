# Standard Library
from typing import Any, TypedDict

# Local Folder
from .track import TrackData


class PlaylistInfoData(TypedDict):
    name: str
    selectedTrack: int


type PlaylistPluginInfoData = dict[str, Any]


class PlaylistData(TypedDict):
    info: PlaylistInfoData
    pluginInfo: PlaylistPluginInfoData
    tracks: list[TrackData]
