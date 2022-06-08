# Future
from __future__ import annotations

# Standard Library
import collections
from typing import TypedDict


__all__ = (
    "EqualizerBandData",
    "EqualizerData",
    "Equalizer",
)


class EqualizerBandData(TypedDict):
    band: int
    gain: float


EqualizerData = list[EqualizerBandData]


class Equalizer:

    __slots__ = ("name", "bands",)

    def __init__(
        self,
        *,
        name: str = "CustomEqualizer",
        bands: list[tuple[int, float]]
    ) -> None:

        if any((band, gain) for band, gain in bands if band < 0 or band > 14 or gain < -0.25 or gain > 1.0):
            raise ValueError("Equalizer bands must be between 0 and 14 and gains must be between -0.25 and 1.0.")

        _dict: collections.defaultdict[float, float] = collections.defaultdict(float)
        _dict.update(bands)

        self.name: str = name
        self.bands: list[EqualizerBandData] = [{"band": band, "gain": _dict[band]} for band in range(15)]

    def __repr__(self) -> str:
        return f"<slate.Equalizer name='{self.name}', bands={self.bands}>"

    def _construct_payload(self) -> EqualizerData:
        return self.bands
