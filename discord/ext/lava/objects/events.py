from ..enums import TrackEndReason, TrackExceptionSeverity
from ..types.payloads import (
    EventPayload, TrackEndEventPayload, TrackExceptionEventPayload, TrackStartEventPayload, TrackStuckEventPayload,
    WebSocketClosedEventPayload,
)


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
        self.type = data["type"]
        self.guild_id = data["guildId"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.BaseEvent guild_id={self.guild_id}>"


class TrackStartEvent(BaseEvent):

    __slots__ = ("encoded_track",)

    def __init__(self, data: TrackStartEventPayload) -> None:
        super().__init__(data)
        self.encoded_track = data["encodedTrack"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackStartEvent guild_id={self.guild_id}, encoded_track={self.encoded_track}>"


class TrackEndEvent(BaseEvent):

    __slots__ = ("encoded_track", "reason",)

    def __init__(self, data: TrackEndEventPayload) -> None:
        super().__init__(data)
        self.encoded_track = data["encodedTrack"]
        self.reason = TrackEndReason(data["reason"])

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackEndEvent guild_id={self.guild_id}, encoded_track={self.encoded_track}, " \
               f"reason={self.reason}>"


class TrackExceptionEvent(BaseEvent):

    __slots__ = ("encoded_track", "message", "severity", "cause",)

    def __init__(self, data: TrackExceptionEventPayload) -> None:
        super().__init__(data)
        self.encoded_track = data["encodedTrack"]

        exception = data["exception"]
        self.message = exception["message"]
        self.severity = TrackExceptionSeverity(exception["severity"])
        self.cause = exception["cause"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackExceptionEvent guild_id={self.guild_id}, encoded_track={self.encoded_track}, " \
               f"message={self.message!r}, severity={self.severity}, cause={self.cause}>"


class TrackStuckEvent(BaseEvent):

    __slots__ = ("encoded_track", "threshold_ms",)

    def __init__(self, data: TrackStuckEventPayload) -> None:
        super().__init__(data)
        self.encoded_track = data["encodedTrack"]
        self.threshold_ms = data["thresholdMs"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.TrackStuckEvent guild_id={self.guild_id}, encoded_track={self.encoded_track}, " \
               f"threshold_ms={self.threshold_ms}>"


class WebSocketClosedEvent(BaseEvent):

    __slots__ = ("code", "reason", "by_remote",)

    def __init__(self, data: WebSocketClosedEventPayload) -> None:
        super().__init__(data)
        self.code = data["code"]
        self.reason = data["reason"]
        self.by_remote = data["byRemote"]

    def __repr__(self) -> str:
        return f"<discord.ext.lava.WebSocketClosedEvent guild_id={self.guild_id}, code={self.code}, " \
               f"reason={self.reason}, by_remote={self.by_remote}>"
