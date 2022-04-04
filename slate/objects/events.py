# Future
from __future__ import annotations

# Standard Library
from typing import Any, Literal

# Local
from ..utils import MISSING


__all__ = (
    "TrackStart",
    "TrackEnd",
    "TrackStuck",
    "TrackException",
    "WebsocketOpen",
    "WebsocketClosed",
)


class BaseEvent:

    def __init__(self, data: dict[str, Any]) -> None:
        self._type: str = MISSING
        self._guild_id: int = int(data.get("guild_id", data.get("guildId")))

    def __repr__(self) -> str:
        return f"<slate.BaseEvent guild_id={self.guild_id}>"

    @property
    def type(self) -> str:
        return self._type

    @property
    def guild_id(self) -> int:
        return self._guild_id


class TrackStart(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__(data)

        self._type: str = "TRACK_START"

        self._track_id: str = data["track"]

    def __repr__(self) -> str:
        return f"<slate.TrackStart guild_id={self.guild_id}, track_id='{self.track_id}'>"

    @property
    def track_id(self) -> str:
        return self._track_id


class TrackEnd(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__(data)

        self._type: str = "TRACK_END"

        self._track_id: str = data["track"]
        self._reason: Literal["STOPPED", "REPLACED", "CLEANUP", "LOAD_FAILED", "FINISHED"] = data["reason"]

    def __repr__(self) -> str:
        return f"<slate.TrackEnd guild_id={self.guild_id}, track_id='{self.track_id}', reason='{self.reason}'>"

    @property
    def track_id(self) -> str:
        return self._track_id

    @property
    def reason(self) -> Literal["STOPPED", "REPLACED", "CLEANUP", "LOAD_FAILED", "FINISHED"]:
        return self._reason


class TrackStuck(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__(data)

        self._type: str = "TRACK_STUCK"

        self._track_id: str = data["track"]
        self._threshold_ms: int = data.get("threshold_ms", data["thresholdMs"])

    def __repr__(self) -> str:
        return f"<slate.TrackStuck guild_id={self.guild_id}, track_id='{self.track_id}', threshold_ms={self.threshold_ms}>"

    @property
    def track_id(self) -> str:
        return self._track_id

    @property
    def threshold_ms(self) -> int:
        return self._threshold_ms


class TrackException(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__(data)

        self._type: str = "TRACK_EXCEPTION"

        self._track_id: str = data["track"]

        exception: dict[str, Any] = data.get("exception", data.get("error"))
        self._message: str = exception["message"]
        self._cause: str = exception["cause"]
        self._severity: Literal["COMMON", "FAULT", "SUSPICIOUS"] = exception["severity"]

    def __repr__(self) -> str:
        return f"<slate.TrackException guild_id={self.guild_id}, track_id='{self.track_id}', message='{self.message}', cause='{self.cause}', " \
               f"severity='{self.severity}'>"

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
    def severity(self) -> Literal["COMMON", "FAULT", "SUSPICIOUS"]:
        return self._severity


class WebsocketOpen(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__(data)

        self._type: str = "WEBSOCKET_OPEN"

        self._target: str = data["target"]
        self._ssrc: int = data["ssrc"]

    def __repr__(self) -> str:
        return f"<slate.WebsocketOpen guild_id={self.guild_id}, target='{self._target}', ssrc={self._ssrc}>"

    @property
    def target(self) -> str:
        return self._target

    @property
    def ssrc(self) -> int:
        return self._ssrc


class WebsocketClosed(BaseEvent):

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__(data)

        self._type: str = "WEBSOCKET_CLOSED"

        self._code: int = data["code"]
        self._reason: str = data["reason"]
        self._by_remote: bool = data["by_remote"]

    def __repr__(self) -> str:
        return f"<slate.WebsocketClosed guild_id={self._guild_id}, code={self._code}, reason='{self._reason}', by_remote={self._by_remote}>"

    @property
    def code(self) -> int:
        return self._code

    @property
    def reason(self) -> str:
        return self._reason

    @property
    def by_remote(self) -> bool:
        return self._by_remote
