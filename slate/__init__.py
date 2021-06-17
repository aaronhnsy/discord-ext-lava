"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
from typing import Final, Literal, NamedTuple

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
    releaselevel: Literal['alpha', 'beta', 'candidate', 'final']
    serial: int


version_info: Final[VersionInfo] = VersionInfo(major=2021, minor=5, micro=26, releaselevel='final', serial=0)


__title__: Final[str] = 'slate'
__author__: Final[str] = 'Axelancerr'
__copyright__: Final[str] = 'Copyright 2020-present Axelancerr'
__license__: Final[str] = 'MIT'
__version__: Final[str] = f'{version_info.major}.{version_info.minor}.{version_info.micro}'
__maintainer__: Final[str] = f'Aaron Hennessey'


logging.getLogger('slate')
