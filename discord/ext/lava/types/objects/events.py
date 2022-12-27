from typing import Literal, TypeAlias, TypedDict

from ..rest import ExceptionData


class TrackStartEventData(TypedDict):
    op: Literal["event"]
    type: Literal["TrackStartEvent"]
    guildId: str
    encodedTrack: str


class TrackEndEventData(TypedDict):
    op: Literal["event"]
    type: Literal["TrackEndEvent"]
    guildId: str
    encodedTrack: str
    reason: Literal["FINISHED", "LOAD_FAILED", "STOPPED", "REPLACED", "CLEANUP"]


class TrackExceptionEventData(TypedDict):
    op: Literal["event"]
    type: Literal["TrackExceptionEvent"]
    guildId: str
    encodedTrack: str
    exception: ExceptionData


class TrackStuckEventData(TypedDict):
    op: Literal["event"]
    type: Literal["TrackStuckEvent"]
    guildId: str
    encodedTrack: str
    thresholdMs: int


class WebsocketClosedEventData(TypedDict):
    op: Literal["event"]
    type: Literal["WebSocketClosedEvent"]
    guildId: str
    code: int
    reason: str
    byRemote: bool


EventData: TypeAlias = TrackStartEventData | TrackEndEventData | TrackExceptionEventData | TrackStuckEventData | WebsocketClosedEventData
