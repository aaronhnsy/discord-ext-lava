import functools
import itertools
import re
from collections.abc import Callable, Iterable
from typing import ParamSpec

import aiohttp
from typing_extensions import TypeVar

from .types.common import JSON, JSONLoads


T = TypeVar("T")
P = ParamSpec("P")


def ordinal(number: int) -> str:
    return "%d%s" % (number, "tsnrhtdd"[(number / 10 % 10 != 1) * (number % 10 < 4) * number % 10::4])


async def json_or_text(response: aiohttp.ClientResponse, json_loads: JSONLoads) -> JSON | str:
    text = await response.text(encoding="utf-8")
    if response.headers.get("Content-Type") in ["application/json", "application/json; charset=utf-8"]:
        return json_loads(text)
    return text


class DeferredMessage:

    def __init__(self, callable: Callable[P, str], *args: P.args, **kwargs: P.kwargs) -> None:
        self.callable: functools.partial[str] = functools.partial(callable, *args, **kwargs)

    def __str__(self) -> str:
        return f"{self.callable()}"


def chunks(iterable: Iterable[T], n: int) -> Iterable[tuple[T, ...]]:
    it = iter(iterable)
    return iter(lambda: tuple(itertools.islice(it, n)), ())


SPOTIFY_REGEX: re.Pattern[str] = re.compile(
    r"(https?://open.)?"
    r"(spotify)"
    r"(.com/|:)"
    r"(?P<type>album|playlist|artist|track)"
    r"([/:])"
    r"(?P<id>[a-zA-Z0-9]+)"
    r"([? &]si = [a-zA-Z0-9]+)?"
    r"([? &]dl_branch=[0-9]+)?"
)
