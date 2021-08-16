from typing import Optional

from aiohttp import ClientResponse

from .objects.enums import SearchType, Source


__all__ = [
    "SlateError",
    "NodeError",
    "NodesNotFound",
    "NodeNotFound",
    "NodeAlreadyExists",
    "NodeConnectionError",
    "NodeNotConnected",
    "HTTPError",
    "NoMatchesFound"
]


class SlateError(Exception):
    pass


class NodeError(SlateError):
    pass


class NodesNotFound(NodeError):
    pass


class NodeNotFound(NodeError):
    pass


class NodeAlreadyExists(NodeError):
    pass


class NodeConnectionError(NodeError):
    pass


class NodeNotConnected(NodeError):
    pass


class HTTPError(SlateError):

    def __init__(
        self,
        message: str,
        response: ClientResponse
    ) -> None:
        super().__init__()

        self._message = message
        self._response = response

    @property
    def message(self) -> str:
        return self._message

    @property
    def response(self) -> ClientResponse:
        return self._response

    @property
    def status(self) -> int:
        return self._response.status


class NoMatchesFound(SlateError):

    def __init__(
        self,
        search: str,
        search_type: SearchType,
        source: Optional[Source] = None
    ) -> None:
        self._search: str = search
        self._search_type = search_type
        self._source: Optional[Source] = source

    @property
    def search(self) -> str:
        return self._search

    @property
    def search_type(self) -> SearchType:
        return self._search_type

    @property
    def source(self) -> Optional[Source]:
        return self._source
