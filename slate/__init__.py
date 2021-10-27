# Future
from __future__ import annotations

# Standard Library
import logging
from typing import Final, Literal, NamedTuple

# My stuff
from slate.exceptions import *
from slate.objects import *
from slate.queue import *
from slate.utils import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: Final[VersionInfo] = VersionInfo(major=2021, minor=10, micro=27, releaselevel="final", serial=0)

__title__: Final[str] = "slate"
__author__: Final[str] = "Axelancerr"
__copyright__: Final[str] = "Copyright 2020-present Axelancerr"
__license__: Final[str] = "MIT"
__version__: Final[str] = "2021.10.27"
__maintainer__: Final[str] = "Aaron Hennessey"
__source__: Final[str] = "https://github.com/Axelancerr/slate"

logging.getLogger("slate")
