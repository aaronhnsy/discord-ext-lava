# Future
from __future__ import annotations

# Standard Library
from typing import Any, Literal

# Packages
import aiohttp

# My stuff
from .objects.enums import Source


__all__ = (
    "SlateError",
    "NodeNotFound",
    "NoNodesConnected",
    "NodeCreationError",
    "NodeNotConnected",
    "NodeConnectionError",
    "NodeInvalidPassword",
    "HTTPError",
    "NoResultsFound",
    "SearchFailed"
)


class SlateError(Exception):
    pass


class NodeNotFound(SlateError):
    pass


class NoNodesConnected(SlateError):
    pass


class NodeCreationError(SlateError):
    pass


class NodeNotConnected(SlateError):
    pass


class NodeConnectionError(SlateError):
    pass


class NodeInvalidPassword(NodeConnectionError):
    pass


#


class HTTPError(SlateError):

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        message: str
    ) -> None:

        self._response: aiohttp.ClientResponse = response
        self._message: str = message

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
        source: Source,
        type: str
    ) -> None:

        self._search: str = search
        self._source: Source = source
        self._type: str = type

    @property
    def search(self) -> str:
        return self._search

    @property
    def source(self) -> Source:
        return self._source

    @property
    def type(self) -> str:
        return self._type


class SearchFailed(SlateError):

    def __init__(
        self,
        data: dict[str, Any]
    ) -> None:

        self._message: str = data["message"]
        self._severity: Literal["COMMON", "FAULT", "SUSPICIOUS"] = data["severity"]

    @property
    def message(self) -> str:
        return self._message

    @property
    def severity(self) -> Literal["COMMON", "FAULT", "SUSPICIOUS"]:
        return self._severity
