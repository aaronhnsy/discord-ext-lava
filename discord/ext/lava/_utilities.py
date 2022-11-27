from collections.abc import Callable


ordinal: Callable[[int], str] = (
    lambda number:
        "%d%s" % (number, "tsnrhtdd"[(number / 10 % 10 != 1) * (number % 10 < 4) * number % 10::4])
)
