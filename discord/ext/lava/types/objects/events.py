from __future__ import annotations

from typing import Literal, TypeAlias, TypedDict


class TrackStartEventPayload(TypedDict):
    op: Literal["event"]
    guildId: str
    type: Literal["TrackStartEvent"]
    encodedTrack: str


class TrackEndEventPayload(TypedDict):
    op: Literal["event"]
    guildId: str
    type: Literal["TrackEndEvent"]
    encodedTrack: str
    reason: Literal["FINISHED", "LOAD_FAILED", "STOPPED", "REPLACED", "CLEANUP"]


class TrackExceptionEventData(TypedDict):
    message: str | None
    severity: Literal["COMMON", "SUSPICIOUS", "FATAL"]
    cause: str


class TrackExceptionEventPayload(TypedDict):
    op: Literal["event"]
    guildId: str
    type: Literal["TrackExceptionEvent"]
    encodedTrack: str
    exception: TrackExceptionEventData


class TrackStuckEventPayload(TypedDict):
    op: Literal["event"]
    guildId: str
    type: Literal["TrackStuckEvent"]
    encodedTrack: str
    thresholdMs: int


class WebsocketClosedEventPayload(TypedDict):
    op: Literal["event"]
    guildId: str
    type: Literal["WebSocketClosedEvent"]
    code: int
    reason: str
    byRemote: bool


EventPayload: TypeAlias = TrackStartEventPayload | TrackEndEventPayload | TrackExceptionEventPayload | TrackStuckEventPayload | WebsocketClosedEventPayload
