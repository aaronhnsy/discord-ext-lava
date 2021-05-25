__title__ = 'slate'
__author__ = 'Axelancerr'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020 Axelancerr'
__version__ = '2021.05.26'

import logging
from collections import namedtuple
from typing import TypeVar, Union

import discord
from discord.ext import commands

from .andesite.node import AndesiteNode
from .bases.node import Node
from .bases.player import Player
from .client import Client
from .exceptions import *
from .lavalink.node import LavalinkNode
from .objects.events import TrackEndEvent, TrackExceptionEvent, TrackStartEvent, TrackStuckEvent, WebSocketClosedEvent
from .objects.filters import BaseFilter, ChannelMix, Distortion, Equalizer, Filter, Karaoke, LowPass, Rotation, Timescale, Tremolo, Vibrato
from .objects.playlist import Playlist
from .objects.routeplanner import FailingAddress, RoutePlannerStatus
from .objects.stats import AndesiteStats, LavalinkStats, Metadata
from .objects.track import Track
from .utils import ExponentialBackoff, Queue


BotType = TypeVar('BotType', bound=Union[discord.Client, commands.Bot, commands.AutoShardedBot])
PlayerType = TypeVar('PlayerType', bound=Union[Player, discord.VoiceProtocol])
NodeType = TypeVar('NodeType', bound=Union[Node, AndesiteNode, LavalinkNode])
ContextType = TypeVar('ContextType', bound=commands.Context)


version_info = namedtuple('VersionInfo', 'major minor micro releaselevel serial')(major=2021, minor=5, micro=26, releaselevel='final', serial=0)
logging.getLogger('slate')
