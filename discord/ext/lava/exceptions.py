from __future__ import annotations

from typing import Any, Literal

import aiohttp

from .objects.enums import Source


__all__ = (
    "LavaError",
    "NodeAlreadyExists",
    "NodeNotFound",
    "NoNodesConnected",
    "NodeAlreadyConnected",
    "NodeConnectionError",
    "InvalidPassword",
    "NodeNotConnected",
    "HTTPError",
    "NoResultsFound",
    "SearchFailed"
)


class LavaError(Exception):
    pass


class NodeAlreadyExists(LavaError):
    pass


class NodeNotFound(LavaError):
    pass


class NoNodesConnected(LavaError):
    pass


class NodeAlreadyConnected(LavaError):
    pass


class NodeConnectionError(LavaError):
    pass


class InvalidPassword(NodeConnectionError):
    pass


class NodeNotConnected(LavaError):
    pass


class HTTPError(LavaError):

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


class NoResultsFound(LavaError):

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


class SearchFailed(LavaError):

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
