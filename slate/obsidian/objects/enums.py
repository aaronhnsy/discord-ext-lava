from enum import Enum


class Op(Enum):

    SUBMIT_VOICE_UPDATE = 0
    STATS = 1

    SETUP_RESUMING = 2
    SETUP_DISPATCH_BUFFER = 3

    PLAYER_EVENT = 4
    PLAYER_UPDATE = 5

    PLAY_TRACK = 6
    STOP_TRACK = 7

    PLAYER_PAUSE = 8
    PLAYER_FILTERS = 9
    PLAYER_SEEK = 10
    PLAYER_DESTROY = 11
    PLAYER_CONFIGURE = 12


class EventType(Enum):
    TRACK_START = 'TRACK_START'
    TRACK_END = 'TRACK_END'
    TRACK_STUCK = 'TRACK_STUCK'
    TRACK_EXCEPTION = 'TRACK_EXCEPTION'
    WEBSOCKET_OPEN = 'WEBSOCKET_OPEN'
    WEBSOCKET_CLOSED = 'WEBSOCKET_CLOSED'


class EndReason(Enum):
    STOPPED = 'STOPPED'
    REPLACED = 'REPLACED'
    CLEANUP = 'CLEANUP'
    LOAD_FAILED = 'LOAD_FAILED'
    FINISHED = 'FINISHED'


class ExceptionSeverity(Enum):
    COMMON = 'COMMON'
    SUSPICIOUS = 'SUSPICIOUS'
    FAULT = 'FAULT'


class TrackSource(Enum):
    YOUTUBE = 'youtube'
    YARN = 'yarn'
    BANDCAMP = 'bandcamp'
    TWITCH = 'twitch'
    VIMEO = 'vimeo'
    NICO = 'nico'
    SOUNDCLOUD = 'soundcloud'
    LOCAL = 'local'
    HTTP = 'http'
    SPOTIFY = 'spotify'
