from typing import Literal, TypedDict

from typing_extensions import NotRequired

from .objects.filters import FiltersData
from .objects.playlist import PlaylistInfoData
from .objects.track import TrackData


HTTPMethod = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"]


class ErrorData(TypedDict):
    timestamp: int
    status: int
    error: str
    trace: NotRequired[str]
    message: str
    path: str


class VoiceStateData(TypedDict):
    token: str
    endpoint: str
    sessionId: str
    connection: NotRequired[bool]
    ping: NotRequired[int]


# GET /v4/sessions/{sessionId}/players
# GET /v4/sessions/{sessionId}/players/{guildId}

class Player(TypedDict):
    guildId: str
    track: TrackData | None
    volume: int
    paused: bool
    voice: VoiceStateData
    filters: FiltersData


# PATCH /v4/sessions/{sessionId}/players/{guildId}

class UpdatePlayerData(TypedDict):
    encodedTrack: NotRequired[str | None]
    identifier: NotRequired[str]
    position: NotRequired[int]
    endTime: NotRequired[int]
    volume: NotRequired[int]
    paused: NotRequired[bool]
    voice: NotRequired[VoiceStateData]
    filters: NotRequired[FiltersData]


# DELETE /v4/sessions/{sessionId}/players/{guildId}
...

# PATCH /v4/sessions/{sessionId}
...


# GET /v4/loadtracks

class ExceptionData(TypedDict):
    message: str | None
    severity: Literal["COMMON", "SUSPICIOUS", "FATAL"]
    cause: str


class TrackLoadingResultData(TypedDict):
    loadType: Literal["TRACK_LOADED", "PLAYLIST_LOADED", "SEARCH_RESULT", "NO_MATCHES", "LOAD_FAILED"]
    playlistInfo: PlaylistInfoData | None
    tracks: list[TrackData]
    exception: ExceptionData | None


# GET /v4/decodetrack
...

# POST /v4/decodetracks
...


# GET /v4/info

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


class LavalinkInfoData(TypedDict):
    version: LavalinkVersionData
    buildTime: int
    git: LavalinkGitData
    jvm: str
    lavaplayer: str
    sourceManagers: list[str]
    filters: list[str]
    plugins: list[LavalinkPluginData]


# GET /v4/stats
...

# GET /version
...


# GET /v4/routeplanner/status

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


RoutePlannerStatusData = TypedDict(
    "RoutePlannerStatusData",
    {
        "class":   Literal["RotatingIpRoutePlanner", "NanoIpRoutePlanner", "RotatingNanoIpRoutePlanner"] | None,
        "details": RoutePlannerDetailsData | None
    }
)

# POST /v4/routeplanner/free/address
...

# POST /v4/routeplanner/free/all
...
