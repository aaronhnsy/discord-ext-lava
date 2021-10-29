# Future
from __future__ import annotations

# Packages
import aiohttp


class SlateError(Exception):
    pass


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
