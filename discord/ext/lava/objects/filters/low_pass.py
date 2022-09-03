from __future__ import annotations

from typing import TypedDict


__all__ = (
    "ObsidianLowPassData",
    "LavalinkLowPassData",
    "LowPass",
)


ObsidianLowPassData = float


class LavalinkLowPassData(TypedDict):
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

    # payloads

    def _construct_obsidian_payload(self) -> ObsidianLowPassData:
        return self.smoothing

    def _construct_lavalink_payload(self) -> LavalinkLowPassData:
        return {
            "smoothing": self.smoothing,
        }
