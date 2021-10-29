# Future
from __future__ import annotations

# Standard Library
from typing import Any

# My stuff
from slate.exceptions import SlateError
from slate.obsidian.objects.enums import ErrorSeverity, SearchType, Source


__all__ = (
    "ObsidianError",
    "NoResultsFound",
    "SearchFailed",
    "NodeError",
    "NodeNotFound",
    "NoNodesFound",
    "NodeAlreadyExists",
    "NodeConnectionError",
    "NodeNotConnected",
)


class ObsidianError(SlateError):
    pass


class NoResultsFound(ObsidianError):

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


class SearchFailed(ObsidianError):

    def __init__(
        self,
        data: dict[str, Any]
    ) -> None:

        self._message: str = data["message"]
        self._severity: ErrorSeverity = ErrorSeverity(data["severity"])

    @property
    def message(self) -> str:
        return self._message

    @property
    def severity(self) -> ErrorSeverity:
        return self._severity


class NodeError(ObsidianError):
    pass


class NodeNotFound(NodeError):
    pass


class NoNodesFound(NodeError):
    pass


class NodeAlreadyExists(NodeError):
    pass


class NodeConnectionError(NodeError):
    pass


class NodeNotConnected(NodeError):
    pass
