from typing import Literal, TypeAlias, TypedDict

from typing_extensions import NotRequired

from ...objects.types.filters import FiltersData
from ...objects.types.playlist import PlaylistData
from ...objects.types.stats import StatsData
from ...objects.types.track import TrackData


# Errors

class ErrorData(TypedDict):
    timestamp: int
    status: int
    error: str
    trace: NotRequired[str]
    message: str
    path: str


# GET: "/v4/sessions/{sessionId}/players"
# GET: "/v4/sessions/{sessionId}/players/{guildId}"
# PATCH: "/v4/sessions/{sessionId}/players/{guildId}"

class VoiceStateData_Response(TypedDict):
    token: str
    endpoint: str
    sessionId: str
    connected: bool
    ping: int


class PlayerData(TypedDict):
    guildId: str
    track: TrackData | None
    volume: int
    paused: bool
    voice: VoiceStateData_Response
    filters: FiltersData


# DELETE: "/v4/sessions/{sessionId}/players/{guildId}"
...


# PATCH: "/v4/sessions/{sessionId}"

class UpdatedSessionData(TypedDict):
    resuming: bool
    timeout: int


# GET "/v4/loadtracks"

class SearchExceptionData(TypedDict):
    message: str | None
    severity: Literal["COMMON", "SUSPICIOUS", "FATAL"]
    cause: str


class SearchData(TypedDict):
    loadType: Literal["TRACK_LOADED", "PLAYLIST_LOADED", "SEARCH_RESULT", "NO_MATCHES", "LOAD_FAILED"]
    playlistInfo: PlaylistData | None
    tracks: list[TrackData]
    exception: SearchExceptionData | None


# GET: "/v4/decodetrack"
DecodedTrackData: TypeAlias = TrackData

# POST: "/v4/decodetracks"
DecodedTracksData: TypeAlias = list[TrackData]


# GET: "/v4/info"

class VersionData(TypedDict):
    semver: str
    major: int
    minor: int
    patch: int
    preRelease: str | None


class GitData(TypedDict):
    branch: str
    commit: str
    commitTime: int


class PluginData(TypedDict):
    name: str
    version: str


class LavalinkInfoData(TypedDict):
    version: VersionData
    buildTime: int
    git: GitData
    jvm: str
    lavaplayer: str
    sourceManagers: list[str]
    filters: list[str]
    plugins: list[PluginData]


# GET: "/v4/stats"
LavalinkStatsData: TypeAlias = StatsData

# GET: "/version"
LavalinkVersionData: TypeAlias = str


# GET: "/v4/routeplanner/status"

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
...

# POST /v4/routeplanner/free/all
...
