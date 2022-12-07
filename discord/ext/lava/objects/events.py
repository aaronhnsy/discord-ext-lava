from __future__ import annotations

from ..enums import TrackEndReason, TrackExceptionSeverity
from ..types import (
    EventPayload, TrackEndEventPayload, TrackExceptionEventData, TrackExceptionEventPayload, TrackStartEventPayload,
    TrackStuckEventPayload, WebsocketClosedEventPayload,
)


__all__ = (
    "TrackStartEvent",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStuckEvent",
    "WebsocketClosedEvent"
)


class _BaseEvent:

    __slots__ = ("type", "guild_id",)

    def __init__(self, data: EventPayload) -> None:
        self.type: str = data["type"]
        self.guild_id: str = data["guildId"]


class TrackStartEvent(_BaseEvent):

    __slots__ = ("encoded_track",)

    def __init__(self, data: TrackStartEventPayload) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackStartEvent guild_id='{self.guild_id}', encoded_track='{self.encoded_track}'>"


class TrackEndEvent(_BaseEvent):

    __slots__ = ("encoded_track", "reason",)

    def __init__(self, data: TrackEndEventPayload) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]
        self.reason: TrackEndReason = TrackEndReason(data["reason"])

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackEndEvent guild_id='{self.guild_id}', encoded_track='{self.encoded_track}', " \
               f"reason={self.reason}>"


class TrackExceptionEvent(_BaseEvent):

    __slots__ = ("encoded_track", "message", "severity", "cause",)

    def __init__(self, data: TrackExceptionEventPayload) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]

        exception: TrackExceptionEventData = data["exception"]
        self.message: str | None = exception["message"]
        self.severity: TrackExceptionSeverity = TrackExceptionSeverity(exception["severity"])
        self.cause: str = exception["cause"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackExceptionEvent guild_id='{self.guild_id}', " \
               f"encoded_track='{self.encoded_track}', message={self.message!r}, severity={self.severity}, " \
               f"cause='{self.cause}'>"


class TrackStuckEvent(_BaseEvent):

    __slots__ = ("encoded_track", "threshold_ms",)

    def __init__(self, data: TrackStuckEventPayload) -> None:
        super().__init__(data)
        self.encoded_track: str = data["encodedTrack"]
        self.threshold_ms: int = data["thresholdMs"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackStuckEvent guild_id='{self.guild_id}', " \
               f"encoded_track='{self.encoded_track}', threshold_ms={self.threshold_ms}>"


class WebsocketClosedEvent(_BaseEvent):

    __slots__ = ("code", "reason", "by_remote",)

    def __init__(self, data: WebsocketClosedEventPayload) -> None:
        super().__init__(data)
        self.code: int = data["code"]
        self.reason: str = data["reason"]
        self.by_remote: bool = data["byRemote"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.WebsocketClosedEvent guild_id='{self.guild_id}', code={self.code}, " \
               f"reason='{self.reason}', by_remote={self.by_remote}>"
