from .enums import ExceptionSeverity


class ObsidianError(Exception):
    pass


class TrackLoadError(ObsidianError):

    def __init__(self, data: dict) -> None:
        super().__init__()

        self._message: str = data.get('message')
        self._severity: ExceptionSeverity = ExceptionSeverity(data.get('severity'))

    @property
    def message(self) -> str:
        return self._message

    @property
    def severity(self) -> ExceptionSeverity:
        return self._severity


class HTTPError(ObsidianError):

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__()

        self._message = message
        self._status_code = status_code

    @property
    def message(self) -> str:
        return self._message

    @property
    def status_code(self) -> int:
        return self._status_code
