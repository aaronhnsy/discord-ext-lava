from __future__ import annotations

from typing import TypedDict


__all__ = (
    "TremoloData",
    "Tremolo",
)


class TremoloData(TypedDict):
    frequency: float
    depth: float


class Tremolo:

    __slots__ = ("frequency", "depth",)

    def __init__(
        self,
        *,
        frequency: float = 2.0,
        depth: float = 0.5
    ) -> None:

        if frequency <= 0.0:
            raise ValueError("'frequency' must be more than 0.0.")
        if depth <= 0.0 or depth > 1.0:
            raise ValueError("'depth' must be more than 0.0 and less than or equal to 1.0.")

        self.frequency: float = frequency
        self.depth: float = depth

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Tremolo frequency={self.frequency}, depth={self.depth}>"

    def _construct_payload(self) -> TremoloData:
        return {
            "frequency": self.frequency,
            "depth":     self.depth
        }
