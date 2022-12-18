from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import NotRequired


HTTPMethod = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"]


class ErrorResponseData(TypedDict):
    timestamp: int
    status: int
    error: str
    trace: NotRequired[str]
    message: str
    path: str
