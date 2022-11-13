from __future__ import annotations


__all__ = (
    "VolumeData",
    "Volume"
)

VolumeData = float


class Volume:

    __slots__ = ("level",)

    def __init__(
        self,
        *,
        level: float = 100.0
    ) -> None:
        self.level: float = level

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Volume level={self.level}>"

    def construct_payload(self) -> VolumeData:
        return self.level / 100.0
