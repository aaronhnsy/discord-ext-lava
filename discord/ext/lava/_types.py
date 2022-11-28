from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import TYPE_CHECKING

import discord
from typing_extensions import Literal, NotRequired, TypeVar, TypedDict

if TYPE_CHECKING:
    from .player import Player  # type: ignore


# Ready OP

class ReadyPayload(TypedDict):
    op: Literal["ready"]
    resumed: bool
    sessionId: str


# Player Update OP

class PlayerStateData(TypedDict):
    time: int
    position: NotRequired[int]
    connected: bool
    ping: int


class PlayerUpdatePayload(TypedDict):
    op: Literal["playerUpdate"]
    guildId: str
    state: PlayerStateData


# Stats OP

class MemoryStatsData(TypedDict):
    free: int
    used: int
    allocated: int
    reservable: int


class CPUStatsData(TypedDict):
    cores: int
    systemLoad: float
    lavalinkLoad: float


class FrameStatsData(TypedDict):
    sent: int
    nulled: int
    deficit: int


class StatsPayload(TypedDict):
    op: Literal["stats"]
    players: int
    playingPlayers: int
    uptime: int
    memory: MemoryStatsData
    cpu: CPUStatsData
    frameStats: FrameStatsData | None


# Event OPs


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


class WebSocketClosedEventPayload(TypedDict):
    op: Literal["event"]
    guildId: str
    type: Literal["WebSocketClosedEvent"]
    code: int
    reason: str
    byRemote: bool


EventPayload = TrackStartEventPayload | TrackEndEventPayload | TrackExceptionEventPayload | TrackStuckEventPayload | WebSocketClosedEventPayload
Payload = ReadyPayload | PlayerUpdatePayload | StatsPayload | EventPayload

EventHandler = Callable[[EventPayload], Awaitable[None]]

JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
JSON_ro = Mapping[str, "JSON_ro"] | Sequence["JSON_ro"] | str | int | float | bool | None

JSONDumps = Callable[[JSON], str]
JSONLoads = Callable[..., JSON]

ClientT = TypeVar("ClientT", bound=discord.Client | discord.AutoShardedClient, default=discord.Client)
PlayerT = TypeVar("PlayerT", bound="Player", default="Player")
