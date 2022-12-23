from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import NotRequired

from .objects.filters import FiltersData


HTTPMethod = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"]


class VoiceStateData(TypedDict):
    token: str
    endpoint: str
    sessionId: str
    connection: NotRequired[bool]
    ping: NotRequired[int]


class UpdatePlayerData(TypedDict):
    encodedTrack: NotRequired[str | None]
    identifier: NotRequired[str]
    position: NotRequired[int]
    endTime: NotRequired[int]
    volume: NotRequired[int]
    paused: NotRequired[bool]
    filters: NotRequired[FiltersData]
    voice: NotRequired[VoiceStateData]


class HTTPErrorData(TypedDict):
    timestamp: int
    status: int
    error: str
    trace: NotRequired[str]
    message: str
    path: str
