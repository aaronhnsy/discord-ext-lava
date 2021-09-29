# Future
from __future__ import annotations

# Packages
import aiohttp

# My stuff
from slate.objects.enums import SearchType, Source


__all__ = (
    "SlateError",
    "HTTPError",
    "NoMatchesFound",
    "NodeError",
    "NodesNotFound",
    "NodeNotFound",
    "NodeAlreadyExists",
    "NodeConnectionError",
    "NodeNotConnected",
)


class SlateError(Exception):
    pass


class HTTPError(SlateError):

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        message: str
    ) -> None:

        self._response = response
        self._message = message

    @property
    def response(self) -> aiohttp.ClientResponse:
        return self._response

    @property
    def message(self) -> str:
        return self._message


class NoMatchesFound(SlateError):

    def __init__(
        self,
        search: str,
        search_type: SearchType,
        source: Source | None = None
    ) -> None:
        self._search: str = search
        self._search_type = search_type
        self._source: Source | None = source

    @property
    def search(self) -> str:
        return self._search

    @property
    def search_type(self) -> SearchType:
        return self._search_type

    @property
    def source(self) -> Source | None:
        return self._source


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
