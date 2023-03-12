from .enums import ExceptionSeverity
from .types.common import ExceptionData


__all__ = [
    "LavaError",
    "LinkAlreadyConnected",
    "LinkConnectionError",
    "LinkNotReady",
    "SearchFailed",
    "NoSearchResults",
]


class LavaError(Exception):
    pass


class LinkAlreadyConnected(LavaError):
    pass


class LinkConnectionError(LavaError):
    pass


class LinkNotReady(LavaError):
    pass


class SearchError(LavaError):
    pass


class SearchFailed(SearchError):

    def __init__(self, exception: ExceptionData) -> None:
        self.message: str | None = exception["message"]
        self.severity: ExceptionSeverity = ExceptionSeverity(exception["severity"])
        self.cause: str = exception["cause"]


class NoSearchResults(SearchError):

    def __init__(self, *, search: str) -> None:
        self.search = search
