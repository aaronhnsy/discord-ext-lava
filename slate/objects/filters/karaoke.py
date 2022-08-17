from __future__ import annotations

from typing import TypedDict


__all__ = (
    "ObsidianKaraokeData",
    "LavalinkKaraokeData",
    "Karaoke",
)


class ObsidianKaraokeData(TypedDict):
    level: float
    mono_level: float
    filter_band: float
    filter_width: float


class LavalinkKaraokeData(TypedDict):
    level: float
    monoLevel: float
    filterBand: float
    filterWidth: float


class Karaoke:

    __slots__ = ("level", "mono_level", "band", "band_width",)

    def __init__(
        self,
        *,
        level: float = 1.0,
        mono_level: float = 1.0,
        band: float = 220.0,
        band_width: float = 100.0
    ) -> None:

        self.level: float = level
        self.mono_level: float = mono_level
        self.band: float = band
        self.band_width: float = band_width

    def __repr__(self) -> str:
        return f"<slate.Karaoke " \
               f"level={self.level}, mono_level={self.mono_level}, " \
               f"band={self.band}, band_width={self.band_width}>"

    def _construct_obsidian_payload(self) -> ObsidianKaraokeData:
        return {
            "level":        self.level,
            "mono_level":   self.mono_level,
            "filter_band":  self.band,
            "filter_width": self.band_width
        }

    def _construct_lavalink_payload(self) -> LavalinkKaraokeData:
        return {
            "level":       self.level,
            "monoLevel":   self.mono_level,
            "filterBand":  self.band,
            "filterWidth": self.band_width
        }
