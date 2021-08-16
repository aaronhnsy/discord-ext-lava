from typing import Any, Optional

from ..exceptions import SlateError
from ..objects.enums import ErrorSeverity


__all__ = ["ObsidianError", "ObsidianSearchError"]


class ObsidianError(SlateError):
    pass


class ObsidianSearchError(ObsidianError):

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__()

        self._message: Optional[str] = data.get("message")
        self._severity: ErrorSeverity = ErrorSeverity(data.get("severity"))

    @property
    def message(self) -> Optional[str]:
        return self._message

    @property
    def severity(self) -> ErrorSeverity:
        return self._severity
