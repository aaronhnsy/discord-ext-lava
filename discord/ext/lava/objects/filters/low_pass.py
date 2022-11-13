from __future__ import annotations

from typing import TypedDict


__all__ = (
    "LowPassData",
    "LowPass",
)


class LowPassData(TypedDict):
    smoothing: float


class LowPass:

    __slots__ = ("smoothing",)

    def __init__(
        self,
        *,
        smoothing: float = 20.0
    ) -> None:
        self.smoothing: float = smoothing

    def __repr__(self) -> str:
        return f"<discord.ext.lava.LowPass smoothing={self.smoothing}>"

    def construct_payload(self) -> LowPassData:
        return {
            "smoothing": self.smoothing,
        }
