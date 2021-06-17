"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Optional

from aiohttp import ClientResponse

from .objects.enums import SearchType, Source


__all__ = ['SlateError', 'NodeError', 'NodesNotFound', 'NodeNotFound', 'NodeAlreadyExists', 'NodeConnectionError', 'NodeNotConnected', 'HTTPError', 'NoMatchesFound']


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

    def __init__(self, message: str, response: ClientResponse) -> None:
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

    def __init__(self, search: str, search_type: SearchType, source: Optional[Source] = None) -> None:
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
