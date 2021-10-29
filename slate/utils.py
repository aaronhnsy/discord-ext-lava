# Future
from __future__ import annotations

# Standard Library
import random
import re
import time
from typing import Any, Literal


__all__ = (
    "ExponentialBackoff",
    "MISSING",
    "SPOTIFY_URL_REGEX"
)


class ExponentialBackoff:

    def __init__(
        self,
        base: int = 1,
        *,
        integral: bool = False
    ) -> None:

        self._base = base

        self._exp = 0
        self._max = 10
        self._reset_time = base * 2 ** 11
        self._last_invocation = time.monotonic()

        rand = random.Random()
        rand.seed()

        self._randfunc = rand.randrange if integral else rand.uniform

    def delay(self) -> float:

        invocation = time.monotonic()
        interval = invocation - self._last_invocation
        self._last_invocation = invocation

        if interval > self._reset_time:
            self._exp = 0

        self._exp = min(self._exp + 1, self._max)
        return self._randfunc(0, self._base * 2 ** self._exp)


class _MissingSentinel:

    def __eq__(self, other: Any) -> Literal[False]:
        return False

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return "..."


MISSING: Any = _MissingSentinel()

SPOTIFY_URL_REGEX: re.Pattern = re.compile(
    r"(https?://open.)?(spotify)(.com/|:)(?P<type>album|playlist|track|artist)([/:])(?P<id>[a-zA-Z0-9]+)(\?si=[a-zA-Z0-9]+)?(&dl_branch=[0-9]+)?"
)
