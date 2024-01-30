# Standard Library
import logging
from typing import Literal, NamedTuple

# Local Folder
from .enums import *
from .exceptions import *
from .link import *
from .objects import *
from .player import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


__version_info__: VersionInfo = VersionInfo(major=1, minor=0, micro=0, releaselevel="alpha", serial=1)
__version__: str = "1.0.0a1"

__title__: str = "discord-ext-lava"
__url__: str = "https://github.com/aaronhnsy/discord-ext-lava"

__author__: str = "Aaron Hennessey (aaronhnsy)"
__email__: str = "aaronhnsy@gmail.com"

__license__: str = "MIT"
__copyright__: str = "Copyright (c) 2019-present Aaron Hennessey (aaronhnsy)"

logging.getLogger("discord.ext.lava")
