# Future
from __future__ import annotations

# Standard Library
import logging
from typing import Final, Literal, NamedTuple

# My stuff
from .exceptions import *
from .node import BaseNode
from .objects.enums import ErrorSeverity, LoadType, QueueLoopMode, SearchType, Source
from .objects.search import SearchResult
from .player import BasePlayer
from .pool import NodePool
from .utils.queue import Queue


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: Final[VersionInfo] = VersionInfo(major=2021, minor=9, micro=25, releaselevel="final", serial=0)

__title__: Final[str] = "slate"
__author__: Final[str] = "Axelancerr"
__copyright__: Final[str] = "Copyright 2020-present Axelancerr"
__license__: Final[str] = "MIT"
__version__: Final[str] = "2021.09.25"
__maintainer__: Final[str] = "Aaron Hennessey"
__source__: Final[str] = "https://github.com/Axelancerr/slate"

logging.getLogger("slate")
