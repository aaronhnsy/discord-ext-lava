from typing import TypeAlias

from .types.events import (
    EventData, EventType, ExceptionData, TrackEndEventData, TrackExceptionEventData, TrackStartEventData,
    TrackStuckEventData, WebSocketClosedEventData,
)
from ..enums import ExceptionSeverity, TrackEndReason


__all__ = [
    "TrackStartEvent",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStuckEvent",
    "WebSocketClosedEvent",
    "Event"
]


class _EventBase:

    __slots__ = ("type", "guild_id",)

    def __init__(self, data: EventData) -> None:
        self.type: EventType = data["type"]
        self.guild_id: str = data["guildId"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.{self.__class__.__name__}: " \
               f"{', '.join(f'{attr}={getattr(self, attr)}' for attr in self.__slots__)}>"


class TrackStartEvent(_EventBase):

    __slots__ = ("encoded_track", )

    def __init__(self, data: TrackStartEventData) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]


class TrackEndEvent(_EventBase):

    __slots__ = ("encoded_track", "reason",)

    def __init__(self, data: TrackEndEventData) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]
        self.reason: TrackEndReason = TrackEndReason(data["reason"])


class TrackExceptionEvent(_EventBase):

    __slots__ = ("encoded_track", "message", "severity", "cause",)

    def __init__(self, data: TrackExceptionEventData) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]

        exception: ExceptionData = data["exception"]
        self.message: str | None = exception["message"]
        self.severity: ExceptionSeverity = ExceptionSeverity(exception["severity"])
        self.cause: str = exception["cause"]


class TrackStuckEvent(_EventBase):

    __slots__ = ("encoded_track", "threshold_ms",)

    def __init__(self, data: TrackStuckEventData) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]
        self.threshold_ms: int = data["thresholdMs"]


class WebSocketClosedEvent(_EventBase):

    __slots__ = ("code", "reason", "by_remote",)

    def __init__(self, data: WebSocketClosedEventData) -> None:
        super().__init__(data)
        self.code: int = data["code"]
        self.reason: str = data["reason"]
        self.by_remote: bool = data["byRemote"]


Event: TypeAlias = TrackStartEvent | TrackEndEvent | TrackExceptionEvent | TrackStuckEvent | WebSocketClosedEvent