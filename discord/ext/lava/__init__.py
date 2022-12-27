import logging
from typing import Literal, NamedTuple

from .enums import *
from .exceptions import *
from .node import *
from .objects import *
from .player import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


__version_info__: VersionInfo = VersionInfo(major=0, minor=6, micro=0, releaselevel="final", serial=0)
__version__: str = "0.6.0"

__title__: str = "discord-ext-lava"
__url__: str = "https://github.com/Axelancerr/discord-ext-lava"

__author__: str = "Aaron Hennessey (Axelancerr)"
__email__: str = "axelancerr@gmail.com"

__license__: str = "MIT"
__copyright__: str = "Copyright (c) 2019-2022 Aaron Hennessey (Axelancerr)"

logging.getLogger("discord-ext-lava")
