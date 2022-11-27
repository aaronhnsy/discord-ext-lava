from .._types.payloads import (
    EventPayload, TrackEndEventPayload, TrackExceptionEventData, TrackExceptionEventPayload, TrackStartEventPayload,
    TrackStuckEventPayload, WebSocketClosedEventPayload,
)
from ..enums import TrackEndReason, TrackExceptionSeverity


__all__ = (
    "BaseEvent",
    "TrackStartEvent",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStuckEvent",
    "WebSocketClosedEvent"
)


class BaseEvent:

    __slots__ = ("type", "guild_id",)

    def __init__(self, data: EventPayload) -> None:
        self.type: str = data["type"]
        self.guild_id: str = data["guildId"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.BaseEvent guild_id={self.guild_id}>"


class TrackStartEvent(BaseEvent):

    __slots__ = ("encoded_track",)

    def __init__(self, data: TrackStartEventPayload) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackStartEvent guild_id={self.guild_id}, encoded_track={self.encoded_track}>"


class TrackEndEvent(BaseEvent):

    __slots__ = ("encoded_track", "reason",)

    def __init__(self, data: TrackEndEventPayload) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]
        self.reason: TrackEndReason = TrackEndReason(data["reason"])

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackEndEvent guild_id={self.guild_id}, encoded_track={self.encoded_track}, " \
               f"reason={self.reason}>"


class TrackExceptionEvent(BaseEvent):

    __slots__ = ("encoded_track", "message", "severity", "cause",)

    def __init__(self, data: TrackExceptionEventPayload) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]

        exception: TrackExceptionEventData = data["exception"]
        self.message: str | None = exception["message"]
        self.severity: TrackExceptionSeverity = TrackExceptionSeverity(exception["severity"])
        self.cause: str = exception["cause"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackExceptionEvent guild_id={self.guild_id}, encoded_track={self.encoded_track}, " \
               f"message={self.message!r}, severity={self.severity}, cause={self.cause}>"


class TrackStuckEvent(BaseEvent):

    __slots__ = ("encoded_track", "threshold_ms",)

    def __init__(self, data: TrackStuckEventPayload) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]
        self.threshold_ms: int = data["thresholdMs"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackStuckEvent guild_id={self.guild_id}, encoded_track={self.encoded_track}, " \
               f"threshold_ms={self.threshold_ms}>"


class WebSocketClosedEvent(BaseEvent):

    __slots__ = ("code", "reason", "by_remote",)

    def __init__(self, data: WebSocketClosedEventPayload) -> None:
        super().__init__(data)
        self.code: int = data["code"]
        self.reason: str = data["reason"]
        self.by_remote: bool = data["byRemote"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.WebSocketClosedEvent guild_id={self.guild_id}, code={self.code}, " \
               f"reason={self.reason}, by_remote={self.by_remote}>"
