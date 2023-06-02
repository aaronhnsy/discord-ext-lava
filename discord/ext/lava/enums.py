import enum


__all__ = [
    "TrackEndReason",
    "ExceptionSeverity",
]


class TrackEndReason(enum.Enum):
    finished = "finished"
    load_failed = "loadFailed"
    stopped = "stopped"
    replaced = "replaced"
    cleanup = "cleanup"


class ExceptionSeverity(enum.Enum):
    common = "common"
    suspicious = "suspicious"
    fatal = "fatal"
