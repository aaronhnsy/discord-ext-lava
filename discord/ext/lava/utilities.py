from collections.abc import Callable


__all__ = (
    "ordinal",
)

ordinal: Callable[[int], str] = lambda n: "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])
