from __future__ import annotations

from typing import Literal, TypeAlias, TypedDict

from typing_extensions import NotRequired

from .objects.events import EventPayload
from .objects.stats import StatsPayload


class ReadyPayload(TypedDict):
    op: Literal["ready"]
    resumed: bool
    sessionId: str


class PlayerStateData(TypedDict):
    time: int
    position: NotRequired[int]
    connected: bool
    ping: int


class PlayerUpdatePayload(TypedDict):
    op: Literal["playerUpdate"]
    guildId: str
    state: PlayerStateData


Payload: TypeAlias = ReadyPayload | PlayerUpdatePayload | StatsPayload | EventPayload
