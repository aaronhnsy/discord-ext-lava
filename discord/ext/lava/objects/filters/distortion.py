from __future__ import annotations

from typing import TypedDict


__all__ = (
    "DistortionData",
    "Distortion",
)


class DistortionData(TypedDict):
    sinOffset: float
    sinScale: float
    cosOffset: float
    cosScale: float
    tanOffset: float
    tanScale: float
    offset: float
    scale: float


class Distortion:

    __slots__ = (
        "sin_offset",
        "sin_scale",
        "cos_offset",
        "cos_scale",
        "tan_offset",
        "tan_scale",
        "offset",
        "scale",
    )

    def __init__(
        self,
        *,
        sin_offset: float = 0.0,
        sin_scale: float = 1.0,
        cos_offset: float = 0.0,
        cos_scale: float = 1.0,
        tan_offset: float = 0.0,
        tan_scale: float = 1.0,
        offset: float = 0.0,
        scale: float = 1.0
    ) -> None:
        self.sin_offset: float = sin_offset
        self.sin_scale: float = sin_scale
        self.cos_offset: float = cos_offset
        self.cos_scale: float = cos_scale
        self.tan_offset: float = tan_offset
        self.tan_scale: float = tan_scale
        self.offset: float = offset
        self.scale: float = scale

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Distortion " \
               f"sin_offset={self.sin_offset}, sin_scale={self.sin_scale}, " \
               f"cos_offset={self.cos_offset}, cos_scale={self.cos_scale}, " \
               f"tan_offset={self.tan_offset}, tan_scale={self.tan_scale}, " \
               f"offset={self.offset}, scale={self.scale}>"

    def construct_payload(self) -> DistortionData:
        return {
            "sinOffset": self.sin_offset,
            "sinScale":  self.sin_scale,
            "cosOffset": self.cos_offset,
            "cosScale":  self.cos_scale,
            "tanOffset": self.tan_offset,
            "tanScale":  self.tan_scale,
            "offset":    self.offset,
            "scale":     self.scale
        }
