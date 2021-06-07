import logging
from typing import NamedTuple

from .client import Client
from .exceptions import *
from .utils import ExponentialBackoff, Queue


logging.getLogger('slate')


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int


version_info = VersionInfo(major=2021, minor=5, micro=26, releaselevel='final', serial=0)

__title__ = 'slate'
__author__ = 'Axelancerr'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020 Axelancerr'
__version__ = f'{version_info.major}.{version_info.major}.{version_info.micro}'
