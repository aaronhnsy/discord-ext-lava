# Future
from __future__ import annotations

# Standard Library
from typing import TypedDict


__all__ = (
    "TimescaleData",
    "Timescale",
)


class TimescaleData(TypedDict):
    pitch: float
    speed: float
    rate: float


class Timescale:

    __slots__ = ("pitch", "speed", "rate",)

    def __init__(
        self,
        *,
        pitch: float = 1.0,
        speed: float = 1.0,
        rate: float = 1.0,
    ) -> None:

        if pitch <= 0.0:
            raise ValueError("'pitch' must be more than 0.0.")
        if speed <= 0.0:
            raise ValueError("'speed' must be more than 0.0.")
        if rate <= 0.0:
            raise ValueError("'rate' must be more than 0.0.")

        self.pitch: float = pitch
        self.speed: float = speed
        self.rate: float = rate

    def __repr__(self) -> str:
        return f"<slate.Timescale pitch={self.pitch}, speed={self.speed}, rate={self.rate}"

    def _construct_payload(self) -> TimescaleData:
        return {
            "pitch": self.pitch,
            "speed": self.speed,
            "rate":  self.rate,
        }
