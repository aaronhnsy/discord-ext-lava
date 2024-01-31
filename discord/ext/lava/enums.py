import enum


__all__ = [
    "TrackEndReason",
    "ExceptionSeverity",
]


class TrackEndReason(enum.Enum):
    FINISHED = "finished"
    LOAD_FAILED = "loadFailed"
    STOPPED = "stopped"
    REPLACED = "replaced"
    CLEANUP = "cleanup"


class ExceptionSeverity(enum.Enum):
    COMMON = "common"
    SUSPICIOUS = "suspicious"
    FATAL = "fatal"
