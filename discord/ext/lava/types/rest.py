from typing import Any, Literal, Never, TypeAlias, TypedDict

from typing_extensions import NotRequired

from .common import ExceptionData
from .objects.filters import FiltersData
from .objects.playlist import PlaylistData
from .objects.stats import StatsData
from .objects.track import TrackData


############
## Errors ##
############
class ErrorRequestParameters(TypedDict):
    trace: NotRequired[bool]


class ErrorData(TypedDict):
    timestamp: int
    status: int
    error: str
    trace: NotRequired[str]
    message: str
    path: str


############
## Common ##
############
class VoiceStateData(TypedDict):
    token: str
    endpoint: str
    sessionId: str


############################################################################
## GET   ## /v4/sessions/{sessionId}/players                              ##
## GET   ## /v4/sessions/{sessionId}/players/{guildId}                    ##
## PATCH ## /v4/sessions/{sessionId}/players/{guildId}?{noReplace=<bool>} ##
############################################################################
class PlayerData(TypedDict):
    guildId: str
    track: TrackData | None
    volume: int
    paused: bool
    voice: VoiceStateData
    filters: FiltersData


############################################################################
## PATCH ## /v4/sessions/{sessionId}/players/{guildId}?{noReplace=<bool>} ##
############################################################################
class UpdatePlayerRequestParameters(TypedDict):
    noReplace: NotRequired[bool]


class UpdatePlayerRequestData(TypedDict):
    encodedTrack: NotRequired[str | None]
    identifier: NotRequired[str]
    position: NotRequired[int]
    endTime: NotRequired[int | None]
    volume: NotRequired[int]
    paused: NotRequired[bool]
    filters: NotRequired[FiltersData]
    voice: NotRequired[VoiceStateData]


#######################################
## PATCH ## /v4/sessions/{sessionId} ##
#######################################
class UpdateSessionRequestData(TypedDict):
    resuming: NotRequired[bool]
    timeout: NotRequired[int]


class SessionData(TypedDict):
    resuming: bool
    timeout: int


##############################################
## GET ## /v4/loadtracks?{identifier=<str>} ##
##############################################
class SearchRequestParameters(TypedDict):
    identifier: str


class TrackLoadedData(TypedDict):
    loadType: Literal["TRACK_LOADED"]
    playlistInfo: None
    pluginInfo: None
    tracks: list[TrackData]
    exception: None


PlaylistPluginData: TypeAlias = dict[str, Any]


class PlaylistLoadedData(TypedDict):
    loadType: Literal["PLAYLIST_LOADED"]
    playlistInfo: PlaylistData
    pluginInfo: PlaylistPluginData
    tracks: list[TrackData]
    exception: None


class SearchResultData(TypedDict):
    loadType: Literal["SEARCH_RESULT"]
    playlistInfo: None
    pluginInfo: None
    tracks: list[TrackData]
    exception: None


class NoMatchesData(TypedDict):
    loadType: Literal["NO_MATCHES"]
    playlistInfo: None
    pluginInfo: None
    tracks: list[Never]
    exception: None


class LoadFailedData(TypedDict):
    loadType: Literal["LOAD_FAILED"]
    playlistInfo: None
    pluginInfo: None
    tracks: list[Never]
    exception: ExceptionData


SearchData = TrackLoadedData | PlaylistLoadedData | SearchResultData | NoMatchesData | LoadFailedData


#########################################################
## GET ## /v4/decodetrack?{encodedTrack=<str(base64)>} ##
#########################################################
class DecodeTrackRequestParameters(TypedDict):
    encodedTrack: str


DecodedTrackData: TypeAlias = TrackData

##############################
## POST ## /v4/decodetracks ##
##############################
DecodeTracksRequestData: TypeAlias = list[str]
DecodedTracksData: TypeAlias = list[DecodedTrackData]


#####################
## GET ## /v4/info ##
#####################
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


######################
## GET ## /v4/stats ##
######################
LavalinkStatsData: TypeAlias = StatsData

#####################
## GET ## /version ##
#####################
LavalinkVersionData: TypeAlias = str


####################################
## GET ## /v4/routeplanner/status ##
####################################
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
        "class":   Literal[
                       "RotatingIpRoutePlanner", "NanoIpRoutePlanner", "RotatingNanoIpRoutePlanner", "BalancingIpRoutePlanner"] | None,
        "details": RoutePlannerDetailsData | None
    }
)


###########################################
## POST ## /v4/routeplanner/free/address ##
###########################################
class FreeAddressRequestData(TypedDict):
    address: str


#######################################
## POST ## /v4/routeplanner/free/all ##
#######################################
...

############
## Types ##
############
RequestMethod: TypeAlias = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"]
RequestHeaders = TypedDict(
    "RequestHeaders",
    {
        "Authorization": str,
        "Content-Type":  NotRequired[Literal["application/json"]]
    }
)
RequestParameters: TypeAlias = (
    ErrorRequestParameters | UpdatePlayerRequestParameters | SearchRequestParameters | DecodeTrackRequestParameters
)
RequestData: TypeAlias = (
    UpdatePlayerRequestData | UpdateSessionRequestData | DecodeTracksRequestData | FreeAddressRequestData
)


class RequestKwargs(TypedDict):
    headers: RequestHeaders
    params: NotRequired[RequestParameters | None]
    data: NotRequired[str | None]
