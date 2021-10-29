# Future
from __future__ import annotations

# Standard Library
from enum import Enum


__all__ = (
    "QueueLoopMode",
)


class QueueLoopMode(Enum):
    OFF = 0
    CURRENT = 1
    QUEUE = 2
