from typing import Literal, TypeAlias, TypedDict

from typing_extensions import NotRequired

from ..objects.types.filters import FiltersData
from ..objects.types.playlist import PlaylistInfoData
from ..objects.types.stats import StatsData
from ..objects.types.track import TrackData


# GET /v4/sessions/{sessionId}/players
# returns 200 - GetPlayerResponseData

class VoiceStateData(TypedDict):
    token: str
    endpoint: str
    sessionId: str
    connection: NotRequired[bool]
    ping: NotRequired[int]


class GetPlayerResponseData(TypedDict):
    guildId: str
    track: TrackData | None
    volume: int
    paused: bool
    voice: VoiceStateData
    filters: FiltersData


# GET /v4/sessions/{sessionId}/players/{guildId}
# returns 200 - GetPlayersResponseData
GetPlayersResponseData: TypeAlias = list[GetPlayerResponseData]


# PATCH /v4/sessions/{sessionId}/players/{guildId}
# returns 200 - UpdatePlayerResponseData

class UpdatePlayerRequestData(TypedDict):
    encodedTrack: NotRequired[str | None]
    identifier: NotRequired[str]
    position: NotRequired[int]
    endTime: NotRequired[int]
    volume: NotRequired[int]
    paused: NotRequired[bool]
    voice: NotRequired[VoiceStateData]
    filters: NotRequired[FiltersData]


UpdatePlayerResponseData: TypeAlias = GetPlayerResponseData


# DELETE /v4/sessions/{sessionId}/players/{guildId}
# returns 204 - no content
...


# PATCH /v4/sessions/{sessionId}
# returns 200 - UpdateSessionResponseData

class UpdateSessionRequestData(TypedDict):
    resuming: NotRequired[bool]
    timeout: NotRequired[int]


class UpdateSessionResponseData(TypedDict):
    resuming: bool
    timeout: int


# GET /v4/loadtracks
# returns 200 - TrackLoadingResponseData

class ExceptionData(TypedDict):
    message: str | None
    severity: Literal["COMMON", "SUSPICIOUS", "FATAL"]
    cause: str


class TrackLoadingResponseData(TypedDict):
    loadType: Literal["TRACK_LOADED", "PLAYLIST_LOADED", "SEARCH_RESULT", "NO_MATCHES", "LOAD_FAILED"]
    playlistInfo: PlaylistInfoData | None
    tracks: list[TrackData]
    exception: ExceptionData | None


# GET /v4/decodetrack
# returns 200 - DecodeTrackResponseData
DecodeTrackResponseData: TypeAlias = TrackData


# POST /v4/decodetracks
# returns 200 - DecodeTracksResponseData
DecodeTracksRequestData: TypeAlias = list[str]
DecodeTracksResponseData: TypeAlias = list[TrackData]


# GET /v4/info
# returns 200 - LavalinkInfoResponseData

class LavalinkVersionData(TypedDict):
    semver: str
    major: int
    minor: int
    patch: int
    preRelease: str | None


class LavalinkGitData(TypedDict):
    branch: str
    commit: str
    commitTime: int


class LavalinkPluginData(TypedDict):
    name: str
    version: str


class LavalinkInfoResponseData(TypedDict):
    version: LavalinkVersionData
    buildTime: int
    git: LavalinkGitData
    jvm: str
    lavaplayer: str
    sourceManagers: list[str]
    filters: list[str]
    plugins: list[LavalinkPluginData]


# GET /v4/stats
StatsResponseData: TypeAlias = StatsData


# GET /version
VersionResponseData: TypeAlias = str


# GET /v4/routeplanner/status
# returns 200 - RoutePlannerStatusResponseData

class IpBlockData(TypedDict):
    type: Literal["Inet4Address", "Inet6Address"]
    size: str


class FailingAddressData(TypedDict):
    address: str
    failingTimestamp: int
    failingTime: str


class RoutePlannerDetailsData(TypedDict):
    ipBlock: IpBlockData
    failingAddresses: list[FailingAddressData]
    rotateIndex: str
    ipIndex: str
    currentAddress: str
    currentAddressIndex: str
    blockIndex: str


RoutePlannerStatusResponseData = TypedDict(
    "RoutePlannerStatusResponseData",
    {
        "class":   Literal["RotatingIpRoutePlanner", "NanoIpRoutePlanner", "RotatingNanoIpRoutePlanner"] | None,
        "details": RoutePlannerDetailsData | None
    }
)


# POST /v4/routeplanner/free/address
# returns 204 - no content

class FreeAddressRequestData(TypedDict):
    address: str


# POST /v4/routeplanner/free/all
# returns 204 - no content
...


class ErrorData(TypedDict):
    timestamp: int
    status: int
    error: str
    trace: NotRequired[str]
    message: str
    path: str


RestMethod: TypeAlias = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"]
RestRequestData: TypeAlias = UpdatePlayerRequestData | UpdateSessionRequestData | DecodeTracksRequestData | FreeAddressRequestData


