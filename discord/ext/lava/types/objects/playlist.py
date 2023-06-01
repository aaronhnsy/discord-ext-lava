from typing import Any, TypeAlias, TypedDict

from .track import TrackData


class PlaylistInfoData(TypedDict):
    name: str
    selectedTrack: int


PlaylistPluginInfoData: TypeAlias = dict[str, Any]


class PlaylistData(TypedDict):
    info: PlaylistInfoData
    pluginInfo: PlaylistPluginInfoData
    tracks: list[TrackData]
