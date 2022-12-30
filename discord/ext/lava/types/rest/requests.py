from typing import Literal, TypeAlias, TypedDict

from typing_extensions import NotRequired

from ...objects.types.filters import FiltersData


# GET: "/v4/sessions/{sessionId}/players" - no request data
...

# GET: "/v4/sessions/{sessionId}/players/{guildId}" - no request data
...


# PATCH: "/v4/sessions/{sessionId}/players/{guildId}"

class UpdatePlayerParameters(TypedDict):
    noReplace: bool


class VoiceStateData_Request(TypedDict):
    token: str
    endpoint: str
    sessionId: str


class UpdatePlayerData(TypedDict):
    encodedTrack: NotRequired[str | None]
    identifier: NotRequired[str]
    position: NotRequired[int]
    endTime: NotRequired[int]
    volume: NotRequired[int]
    paused: NotRequired[bool]
    voice: NotRequired[VoiceStateData_Request]
    filters: NotRequired[FiltersData]


# DELETE: "/v4/sessions/{sessionId}/players/{guildId}" - no request data
...


# PATCH: "/v4/sessions/{sessionId}"

class UpdateSessionData(TypedDict):
    resuming: NotRequired[bool]
    timeout: NotRequired[int]


# GET: "/v4/loadtracks"

class SearchParameters(TypedDict):
    identifier: str


# GET: "/v4/decodetrack"

class DecodeTrackParameters(TypedDict):
    encodedTrack: str


# POST: "/v4/decodetracks"
DecodeTracksData: TypeAlias = list[str]

# GET: "/v4/info"
...

# GET: "/v4/stats"
...

# GET: "/version"
...

# GET: "/v4/routeplanner/status"
...


# POST: "/v4/routeplanner/free/address"

class FreeAddressData(TypedDict):
    address: str


# POST: "/v4/routeplanner/free/all"
...


# Errors

class ErrorParameters(TypedDict):
    trace: bool


# Common

RequestMethod: TypeAlias = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"]

RequestHeaders = TypedDict(
    "RequestHeaders",
    {
        "Authorization": str,
        "Content-Type":  NotRequired[Literal["application/json"]]
    }
)
RequestParameters: TypeAlias = (
    UpdatePlayerParameters | SearchParameters | DecodeTrackParameters | ErrorParameters
)
RequestData: TypeAlias = (
    UpdatePlayerData | UpdateSessionData | DecodeTracksData | FreeAddressData
)


class RequestKwargs(TypedDict):
    headers: RequestHeaders
    params: NotRequired[RequestParameters | None]
    data: NotRequired[str | None]
