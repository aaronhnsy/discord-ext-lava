from __future__ import annotations

import random
import re
from collections.abc import Callable
from typing import Any, Literal

from .objects.enums import Source


__all__ = (
    "SPOTIFY_URL_REGEX",
    "MISSING",
)


SPOTIFY_URL_REGEX: re.Pattern[str] = re.compile(
    r"(http(s)?://open.)?"
    r"(spotify)"
    r"(.com/|:)(?P<type>album|playlist|artist|track)"
    r"([/:])(?P<id>[a-zA-Z0-9]+)"
    r"([?&]si=[a-zA-Z0-9]+)?([?&]dl_branch=[0-9]+)?"
)

OBSIDIAN_TO_LAVALINK_OP_MAP: dict[int, str] = {
    0:  "voiceUpdate",
    1:  "stats",
    2:  "configureResuming",
    3:  "configureDispatchBuffer",
    4:  "event",
    5:  "playerUpdate",
    6:  "play",
    7:  "stop",
    8:  "pause",
    9:  "filters",
    10: "seek",
    11: "destroy"
}

SOURCE_MAP: dict[Source, str] = {
    Source.Youtube:      "ytsearch:",
    Source.YoutubeMusic: "ytmsearch:",
    Source.SoundCloud:   "scsearch:",
}

NO_MATCHES: set[str] = {"NONE", "NO_MATCHES"}
LOAD_FAILED: set[str] = {"FAILED", "LOAD_FAILED"}
TRACK_LOADED: set[str] = {"TRACK", "TRACK_LOADED", "SEARCH_RESULT"}
PLAYLIST_LOADED: set[str] = {"TRACK_COLLECTION", "PLAYLIST_LOADED"}

ordinal: Callable[[int], str] = lambda n: "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


"""
https://github.com/PythonistaGuild/Wavelink/blob/fe27c9175e03ce42ea55ad47a4cb7b02bd1324d7/wavelink/backoff.py#L29-L75

The MIT License (MIT)

Copyright (c) 2021 PythonistaGuild, EvieePy, Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


class Backoff:

    def __init__(
        self,
        *,
        base: int = 1,
        max_time: float,
        max_tries: int | None
    ) -> None:

        self._base: int = base
        self._max_wait: float = max_time
        self._max_tries: int | None = max_tries

        _random = random.Random()
        _random.seed()
        self._uniform: Callable[[float, float], float] = _random.uniform

        self._tries: int = 0
        self._last_wait: float = 0

    def calculate(self) -> float:

        self._tries += 1

        exponent = min((self._tries ** 2), self._max_wait)
        wait = self._uniform(0, (self._base * 2) * exponent)

        if wait <= self._last_wait:
            wait = self._last_wait * 2

        self._last_wait = wait

        if wait > self._max_wait:
            wait = self._max_wait

        if self._max_tries and self._tries > self._max_tries:
            self._tries = 0
            self._last_wait = 0

        return wait


"""
https://github.com/Rapptz/discord.py/blob/45d498c1b76deaf3b394d17ccf56112fa691d160/discord/utils.py#L92-L103

The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


class _MissingSentinel:

    def __eq__(self, other: Any) -> Literal[False]:
        return False

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return "<MISSING>"


MISSING: Any = _MissingSentinel()
