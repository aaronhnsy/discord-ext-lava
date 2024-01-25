from typing import Literal, TypedDict

from .track import TrackData
from ..common import ExceptionData


class TrackStartEventData(TypedDict):
    op: Literal["event"]
    type: Literal["TrackStartEvent"]
    guildId: str
    track: TrackData


class TrackEndEventData(TypedDict):
    op: Literal["event"]
    type: Literal["TrackEndEvent"]
    guildId: str
    track: TrackData
    reason: Literal["finished", "loadFailed", "stopped", "replaced", "cleanup"]


class TrackExceptionEventData(TypedDict):
    op: Literal["event"]
    type: Literal["TrackExceptionEvent"]
    guildId: str
    track: TrackData
    exception: ExceptionData


class TrackStuckEventData(TypedDict):
    op: Literal["event"]
    type: Literal["TrackStuckEvent"]
    guildId: str
    track: TrackData
    thresholdMs: int


class WebSocketClosedEventData(TypedDict):
    op: Literal["event"]
    type: Literal["WebSocketClosedEvent"]
    guildId: str
    code: int
    reason: str
    byRemote: bool


type EventType = Literal[
    "TrackStartEvent",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStuckEvent",
    "WebSocketClosedEvent"
]
type TrackEventData = TrackStartEventData | TrackEndEventData | TrackExceptionEventData | TrackStuckEventData
type EventData = TrackEventData | WebSocketClosedEventData
