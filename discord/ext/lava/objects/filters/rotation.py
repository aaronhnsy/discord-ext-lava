from __future__ import annotations

from typing import TypedDict


__all__ = (
    "RotationData",
    "Rotation",
)


class RotationData(TypedDict):
    rotationHz: float


class Rotation:

    __slots__ = ("speed",)

    def __init__(
        self,
        *,
        speed: float = 5.0
    ) -> None:
        self.speed: float = speed

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Rotation speed={self.speed}>"

    def construct_payload(self) -> RotationData:
        return {
            "rotationHz": self.speed,
        }
