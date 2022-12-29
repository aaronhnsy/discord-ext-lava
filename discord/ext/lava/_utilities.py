import re
from collections.abc import Callable


ordinal: Callable[[int], str] = (
    lambda number:
        "%d%s" % (number, "tsnrhtdd"[(number / 10 % 10 != 1) * (number % 10 < 4) * number % 10::4])
)

spotify_url_regex: re.Pattern[str] = re.compile(
    r"(https?://open.)?"
    r"(spotify)"
    r"(.com/|:)"
    r"(?P<type>album|playlist|artist|track)"
    r"([/:])"
    r"(?P<id>[a-zA-Z0-9]+)"
    r"([? &]si = [a-zA-Z0-9]+)?"
    r"([? &]dl_branch=[0-9]+)?"
)
