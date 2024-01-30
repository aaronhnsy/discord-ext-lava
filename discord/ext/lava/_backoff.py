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

# Standard Library
import random
from collections.abc import Callable


class Backoff:

    def __init__(
        self,
        *,
        base: int = 1,
        max_time: float,
        max_tries: int | None
    ) -> None:

        self.base: int = base
        self.max_wait: float = max_time
        self.max_tries: int | None = max_tries

        self.tries: int = 0
        self.last_wait: float = 0

        _random = random.Random()
        _random.seed()
        self.uniform: Callable[[float, float], float] = _random.uniform

    def reset(self) -> None:
        self.tries = 0

    def calculate(self) -> float:

        self.tries += 1

        exponent = min((self.tries ** 2), self.max_wait)
        wait = self.uniform(0, (self.base * 2) * exponent)

        if wait <= self.last_wait:
            wait = self.last_wait * 2

        self.last_wait = wait
        wait = min(wait, self.max_wait)

        if self.max_tries and self.tries > self.max_tries:
            self.tries = 0
            self.last_wait = 0

        return wait
