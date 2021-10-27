# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp

# My stuff
from slate.objects.enums import ErrorSeverity, SearchType, Source


__all__ = (
    "SlateError",
    "HTTPError",
    "NoResultsFound",
    "SearchFailed",
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


class NoResultsFound(SlateError):

    def __init__(
        self,
        *,
        search: str,
        search_source: Source,
        search_type: SearchType
    ) -> None:

        self._search: str = search
        self._search_source: Source = search_source
        self._search_type: SearchType = search_type

    @property
    def search(self) -> str:
        return self._search

    @property
    def search_source(self) -> Source:
        return self._search_source

    @property
    def search_type(self) -> SearchType:
        return self._search_type


class SearchFailed(SlateError):

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__()

        self._message: str = data["message"]
        self._severity: ErrorSeverity = ErrorSeverity(data["severity"])

    @property
    def message(self) -> str:
        return self._message

    @property
    def severity(self) -> ErrorSeverity:
        return self._severity


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
