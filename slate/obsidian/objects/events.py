# Future
from __future__ import annotations

# Standard Library
from typing import Any

# My stuff
from slate.objects.enums import ErrorSeverity
from slate.obsidian.objects.enums import EventType, TrackEndReason


__all__ = (
    "BaseEvent",
    "WebsocketOpen",
    "WebsocketClosed",
    "TrackStart",
    "TrackEnd",
    "TrackStuck",
    "TrackException",
)


class BaseEvent:

    def __init__(self, data: dict[str, Any]) -> None:

        self._type: EventType = EventType(data["type"])
        self._guild_id: int = int(data["guild_id"])

    def __repr__(self) -> str:
        return f"<slate.obsidian.BaseEvent guild_id={self.guild_id}>"

    #

    @property
    def type(self) -> EventType:
        return self._type

    @property
    def guild_id(self) -> int:
        return self._guild_id


class WebsocketOpen(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__(data)

        self._target: str = data["target"]
        self._ssrc: int = data["ssrc"]

    def __repr__(self) -> str:
        return f"<slate.obsidian.WebsocketOpen guild_id={self.guild_id}>"

    #

    @property
    def target(self) -> str:
        return self._target

    @property
    def ssrc(self) -> int:
        return self._ssrc


class WebsocketClosed(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:

        super().__init__(data)

        self._reason: str | None = data["reason"]
        self._code: int = data["code"]
        self._by_remote: bool = data["by_remote"]

    def __repr__(self) -> str:
        return f"<slate.obsidian.WebsocketClosed guild_id={self.guild_id}>"

    #

    @property
    def reason(self) -> str | None:
        return self._reason

    @property
    def code(self) -> int:
        return self._code

    @property
    def by_remote(self) -> bool:
        return self._by_remote


class TrackStart(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:

        super().__init__(data)

        self._track_id: str = data["track"]

    def __repr__(self) -> str:
        return f"<slate.obsidian.TrackStart guild_id={self.guild_id}, track_id='{self.track_id}'>"

    #

    @property
    def track_id(self) -> str:
        return self._track_id


class TrackEnd(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:

        super().__init__(data)

        self._track_id: str = data["track"]

        self._reason: TrackEndReason = TrackEndReason(data["reason"])

    def __repr__(self) -> str:
        return f"<slate.obsidian.TrackEnd guild_id={self.guild_id}, track_id='{self.track_id}', reason='{self.reason}'>"

    #

    @property
    def track_id(self) -> str:
        return self._track_id

    @property
    def reason(self) -> TrackEndReason:
        return self._reason


class TrackStuck(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:

        super().__init__(data)

        self._track_id: str = data["track"]

        self._threshold_ms: int = data["threshold_ms"]

    def __repr__(self) -> str:
        return f"<slate.obsidian.TrackStuck guild_id={self.guild_id}, track_id='{self.track_id}', threshold_ms={self.threshold_ms}>"

    #

    @property
    def track_id(self) -> str:
        return self._track_id

    @property
    def threshold_ms(self) -> int:
        return self._threshold_ms


class TrackException(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:

        super().__init__(data)

        self._track_id: str = data["track"]

        exception: dict[str, Any] = data["exception"]
        self._message: str = exception["message"]
        self._cause: str = exception["cause"]
        self._severity: ErrorSeverity = ErrorSeverity(exception["severity"])

    def __repr__(self) -> str:
        return f"<slate.obsidian.TrackException guild_id={self.guild_id}, track_id='{self.track_id}', severity='{self.severity}', cause='{self.cause}', " \
               f"message='{self.message}'>"

    #

    @property
    def track_id(self) -> str:
        return self._track_id

    @property
    def message(self) -> str:
        return self._message

    @property
    def cause(self) -> str:
        return self._cause

    @property
    def severity(self) -> ErrorSeverity:
        return self._severity
