# Future
from __future__ import annotations

# Standard Library
from typing import Any

# My stuff
from slate.exceptions import SlateError
from slate.objects import ErrorSeverity


__all__ = ["ObsidianError", "ObsidianSearchError"]


class ObsidianError(SlateError):
    pass


class ObsidianSearchError(ObsidianError):

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__()

        self._message: str | None = data.get("message")
        self._severity: ErrorSeverity = ErrorSeverity(data.get("severity"))

    @property
    def message(self) -> str | None:
        return self._message

    @property
    def severity(self) -> ErrorSeverity:
        return self._severity
