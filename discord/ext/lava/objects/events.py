from __future__ import annotations

from ..enums import ExceptionSeverity, TrackEndReason
from ..types.objects.events import EventData, EventType, TrackEndEventData, TrackEventData
from ..types.objects.events import TrackExceptionEventData, TrackStuckEventData, WebSocketClosedEventData
from .track import Track


__all__ = [
    "TrackStartEvent",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStuckEvent",
    "WebSocketClosedEvent",
    "UnhandledEvent",
]


class _BaseEvent:
    __slots__ = ("type", "guild_id", "_dispatch_name",)

    def __init__(self, data: EventData) -> None:
        self.type: EventType = data["type"]
        self.guild_id: str = data["guildId"]


class _BaseTrackEvent(_BaseEvent):
    __slots__ = ("track",)

    def __init__(self, data: TrackEventData) -> None:
        super().__init__(data)
        self.track: Track = Track(data["track"])


class TrackStartEvent(_BaseTrackEvent):

    def __repr__(self) -> str:
        return f"<lava.{self.__class__.__name__}: track='{self.track}'>"


class TrackEndEvent(_BaseTrackEvent):
    __slots__ = ("reason",)

    def __init__(self, data: TrackEndEventData) -> None:
        super().__init__(data)
        self.reason: TrackEndReason = TrackEndReason(data["reason"])

    def __repr__(self) -> str:
        return f"<lava.{self.__class__.__name__}: track='{self.track}', reason={self.reason}>"


class TrackExceptionEvent(_BaseTrackEvent):
    __slots__ = ("message", "severity", "cause",)

    def __init__(self, data: TrackExceptionEventData) -> None:
        super().__init__(data)
        exception = data["exception"]
        self.message: str | None = exception["message"]
        self.severity: ExceptionSeverity = ExceptionSeverity(exception["severity"])
        self.cause: str = exception["cause"]

    def __repr__(self) -> str:
        return f"<lava.{self.__class__.__name__}: track='{self.track}', message='{self.message}' " \
               f"severity='{self.severity}' cause='{self.cause}'>"


class TrackStuckEvent(_BaseTrackEvent):
    __slots__ = ("threshold_ms",)

    def __init__(self, data: TrackStuckEventData) -> None:
        super().__init__(data)
        self.threshold_ms: int = data["thresholdMs"]

    def __repr__(self) -> str:
        return f"<lava.{self.__class__.__name__}: track='{self.track}', threshold_ms={self.threshold_ms}>"


class WebSocketClosedEvent(_BaseEvent):
    __slots__ = ("code", "reason", "by_remote",)

    def __init__(self, data: WebSocketClosedEventData) -> None:
        super().__init__(data)
        self.code: int = data["code"]
        self.reason: str = data["reason"]
        self.by_remote: bool = data["byRemote"]

    def __repr__(self) -> str:
        return f"<lava.{self.__class__.__name__}: code={self.code}, reason='{self.reason}', " \
               f"by_remote={self.by_remote}>"


class UnhandledEvent(_BaseEvent):
    __slots__ = ("data",)

    def __init__(self, data: EventData) -> None:
        super().__init__(data)
        self.data: EventData = data

    def __repr__(self) -> str:
        return f"<lava.{self.__class__.__name__}: data={self.data}>"
