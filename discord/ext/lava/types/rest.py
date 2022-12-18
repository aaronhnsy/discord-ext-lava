from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import NotRequired


HTTPMethod = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"]


class VoiceStateData(TypedDict):
    token: str
    endpoint: str
    sessionId: str
    connection: NotRequired[bool]
    ping: NotRequired[int]


class HTTPRequestData(TypedDict):
    voice: NotRequired[VoiceStateData]


class HTTPErrorData(TypedDict):
    timestamp: int
    status: int
    error: str
    trace: NotRequired[str]
    message: str
    path: str
