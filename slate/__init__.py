__title__ = 'slate'
__author__ = 'Axelancerr'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020 Axelancerr'
__version__ = '0.2.0'

import logging
from collections import namedtuple

from .andesite.node import AndesiteNode
from .bases.node import BaseNode
from .bases.player import BasePlayer
from .client import Client
from .exceptions import *
from .lavalink.node import LavalinkNode
from .objects.events import TrackEndEvent, TrackExceptionEvent, TrackStartEvent, TrackStuckEvent, WebSocketClosedEvent
from .objects.filters import BaseFilter, ChannelMix, Distortion, Equalizer, Filter, Karaoke, LowPass, Rotation, Timescale, Tremolo, Vibrato
from .objects.playlist import Playlist
from .objects.stats import AndesiteStats, LavalinkStats, Metadata
from .objects.track import Track
from .utils import ExponentialBackoff, Queue

version_info = namedtuple('VersionInfo', 'major minor micro releaselevel serial')(major=0, minor=2, micro=0, releaselevel='alpha', serial=0)
logging.getLogger('slate')
