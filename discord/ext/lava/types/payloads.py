from typing_extensions import Literal, NotRequired, TypedDict


# Ready OP

class ReadyPayload(TypedDict):
    op: Literal["ready"]
    resumed: NotRequired[bool]
    sessionId: str


# Player OP

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


# Event OP

class _BaseEvent(TypedDict):
    op: Literal["event"]
    guildId: str


class TrackStartEventPayload(_BaseEvent):
    type: Literal["TrackStartEvent"]
    encodedTrack: str


class TrackEndEventPayload(_BaseEvent):
    type: Literal["TrackEndEvent"]
    encodedTrack: str
    reason: Literal["FINISHED", "LOAD_FAILED", "STOPPED", "REPLACED", "CLEANUP"]


class TrackExceptionData(TypedDict):
    message: str | None
    severity: Literal["COMMON", "SUSPICIOUS", "FATAL"]
    cause: str


class TrackExceptionEventPayload(_BaseEvent):
    type: Literal["TrackExceptionEvent"]
    encodedTrack: str
    exception: TrackExceptionData


class TrackStuckEventPayload(_BaseEvent):
    type: Literal["TrackStuckEvent"]
    encodedTrack: str
    thresholdMs: int


class WebSocketClosedEventPayload(_BaseEvent):
    type: Literal["WebSocketClosedEvent"]
    code: int
    reason: str
    byRemote: bool


EventPayload = TrackStartEventPayload | TrackEndEventPayload | TrackExceptionEventPayload | TrackStuckEventPayload | WebSocketClosedEventPayload
Payload = ReadyPayload | PlayerUpdatePayload | StatsPayload | EventPayload
