from __future__ import annotations

from typing import TYPE_CHECKING

from .._utilities import get_event_dispatch_name
from ..enums import ExceptionSeverity, TrackEndReason
from .track import Track


if TYPE_CHECKING:
    from ..types.objects.events import EventData, EventType, TrackEndEventData, TrackEventData
    from ..types.objects.events import TrackExceptionEventData, TrackStuckEventData, WebSocketClosedEventData


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
        self._dispatch_name: str = get_event_dispatch_name(self.type)

    def __repr__(self) -> str:
        attributes = [f"{x}='{getattr(self, x)}'" for x in self.__slots__ if not x.startswith("_")]
        return f"<discord.ext.lava.{self.__class__.__name__}: {", ".join(attributes)}>"


class _TrackEvent(_BaseEvent):
    __slots__ = ("track",)

    def __init__(self, data: TrackEventData) -> None:
        super().__init__(data)
        self.track: Track = Track(data["track"])


class TrackStartEvent(_TrackEvent):
    pass


class TrackEndEvent(_TrackEvent):
    __slots__ = ("reason",)

    def __init__(self, data: TrackEndEventData) -> None:
        super().__init__(data)
        self.reason: TrackEndReason = TrackEndReason(data["reason"])


class TrackExceptionEvent(_TrackEvent):
    __slots__ = ("message", "severity", "cause",)

    def __init__(self, data: TrackExceptionEventData) -> None:
        super().__init__(data)
        exception = data["exception"]
        self.message: str | None = exception["message"]
        self.severity: ExceptionSeverity = ExceptionSeverity(exception["severity"])
        self.cause: str = exception["cause"]


class TrackStuckEvent(_TrackEvent):
    __slots__ = ("threshold_ms",)

    def __init__(self, data: TrackStuckEventData) -> None:
        super().__init__(data)
        self.threshold_ms: int = data["thresholdMs"]


class WebSocketClosedEvent(_BaseEvent):
    __slots__ = ("code", "reason", "by_remote",)

    def __init__(self, data: WebSocketClosedEventData) -> None:
        super().__init__(data)
        self.code: int = data["code"]
        self.reason: str = data["reason"]
        self.by_remote: bool = data["byRemote"]


class UnhandledEvent(_BaseEvent):
    __slots__ = ("data",)

    def __init__(self, data: EventData) -> None:
        super().__init__(data)
        self.data: EventData = data
