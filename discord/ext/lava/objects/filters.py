from __future__ import annotations

import abc
import collections

from .types.filters import (
    ChannelMixData, DistortionData, EqualizerData, FiltersData, KaraokeData, LowPassData, RotationData, TimescaleData,
    TremoloData, VibratoData,
)


__all__ = [
    "Equalizer",
    "Karaoke",
    "Timescale",
    "Tremolo",
    "Vibrato",
    "Rotation",
    "Distortion",
    "ChannelMix",
    "LowPass",
    "Filter",
]


class _FilterBase(metaclass=abc.ABCMeta):

    __slots__ = ()

    def __repr__(self) -> str:
        return f"<discord.ext.lava.{self.__class__.__name__} " \
               f"{', '.join(f'{attr[1:]}={getattr(self, attr)}' for attr in self.__slots__)}>"

    @property
    @abc.abstractmethod
    def data(self) -> ...:
        raise NotImplementedError


class Equalizer(_FilterBase):

    __slots__ = ("_bands",)

    def __init__(self, *, bands: list[tuple[int, float]] | None = None) -> None:
        self._bands: collections.defaultdict[int, float] = collections.defaultdict(float)

        if bands:
            if any((band, gain) for band, gain in bands if band < 0 or band > 14 or gain < -0.25 or gain > 1.0):
                raise ValueError("Equalizer bands must be between 0 and 14 and gains must be between -0.25 and 1.0.")
            self._bands.update(bands)

    @property
    def data(self) -> EqualizerData:
        return [{"band": band, "gain": self._bands[band]} for band in range(15)]


class Karaoke(_FilterBase):

    __slots__ = ("_level", "_mono_level", "_filter_band", "_filter_width",)

    def __init__(
        self,
        *,
        level: float = 1.0,
        mono_level: float = 1.0,
        filter_band: float = 220.0,
        filter_width: float = 100.0
    ) -> None:
        self._level: float = level
        self._mono_level: float = mono_level
        self._filter_band: float = filter_band
        self._filter_width: float = filter_width

    @property
    def data(self) -> KaraokeData:
        return {
            "level":       self._level,
            "monoLevel":   self._mono_level,
            "filterBand":  self._filter_band,
            "filterWidth": self._filter_width,
        }


class Timescale(_FilterBase):

    __slots__ = ("_pitch", "_speed", "_rate",)

    def __init__(
        self,
        *,
        pitch: float = 1.0,
        speed: float = 1.0,
        rate: float = 1.0,
    ) -> None:

        if pitch < 0.0:
            raise ValueError("'pitch' must be more than or equal to 0.0.")
        if speed < 0.0:
            raise ValueError("'speed' must be more than or equal to 0.0.")
        if rate < 0.0:
            raise ValueError("'rate' must be more than or equal to 0.0.")

        self._pitch: float = pitch
        self._speed: float = speed
        self._rate: float = rate

    @property
    def data(self) -> TimescaleData:
        return {
            "pitch": self._pitch,
            "speed": self._speed,
            "rate":  self._rate
        }


class Tremolo(_FilterBase):

    __slots__ = ("_frequency", "_depth",)

    def __init__(
        self,
        *,
        frequency: float = 2.0,
        depth: float = 0.0
    ) -> None:

        if frequency <= 0.0:
            raise ValueError("'frequency' must be more than 0.0.")
        if depth <= 0.0 or depth > 1.0:
            raise ValueError("'depth' must be more than 0.0 and less than or equal to 1.0.")

        self._frequency: float = frequency
        self._depth: float = depth

    @property
    def data(self) -> TremoloData:
        return {
            "frequency": self._frequency,
            "depth":     self._depth,
        }


class Vibrato(_FilterBase):

    __slots__ = ("_frequency", "_depth",)

    def __init__(
        self,
        *,
        frequency: float = 2.0,
        depth: float = 0.0
    ) -> None:

        if frequency <= 0.0 or frequency > 14.0:
            raise ValueError("'frequency' must be more than 0.0 and less than or equal to 14.0.")
        if depth <= 0.0 or depth > 1.0:
            raise ValueError("'depth' must be more than 0.0 and less than or equal to 1.0.")

        self._frequency: float = frequency
        self._depth: float = depth

    @property
    def data(self) -> VibratoData:
        return {
            "frequency": self._frequency,
            "depth":     self._depth,
        }


class Rotation(_FilterBase):

    __slots__ = ("_speed",)

    def __init__(self, *, speed: float = 0.0) -> None:
        self._speed: float = speed

    @property
    def data(self) -> RotationData:
        return {"rotationHz": self._speed}


class Distortion(_FilterBase):

    __slots__ = (
        "_sin_offset", "_sin_scale", "_cos_offset", "_cos_scale", "_tan_offset", "_tan_scale", "_offset", "_scale",
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
        self._sin_offset: float = sin_offset
        self._sin_scale: float = sin_scale
        self._cos_offset: float = cos_offset
        self._cos_scale: float = cos_scale
        self._tan_offset: float = tan_offset
        self._tan_scale: float = tan_scale
        self._offset: float = offset
        self._scale: float = scale

    @property
    def data(self) -> DistortionData:
        return {
            "sinOffset": self._sin_offset,
            "sinScale":  self._sin_scale,
            "cosOffset": self._cos_offset,
            "cosScale":  self._cos_scale,
            "tanOffset": self._tan_offset,
            "tanScale":  self._tan_scale,
            "offset":    self._offset,
            "scale":     self._scale,
        }


class ChannelMix(_FilterBase):

    __slots__ = ("_left_to_left", "_left_to_right", "_right_to_left", "_right_to_right",)

    def __init__(
        self,
        *,
        left_to_left: float = 1.0,
        left_to_right: float = 0.0,
        right_to_left: float = 0.0,
        right_to_right: float = 1.0,
    ) -> None:

        if any(
            value for value in (left_to_left, left_to_right, right_to_left, right_to_right)
            if value < 0.0 or value > 1.0
        ):
            raise ValueError(
                "'left_to_left', 'left_to_right', 'right_to_left', and 'right_to_right' "
                "must all be more than or equal to 0.0 and less than or equal to 1.0"
            )

        self._left_to_left: float = left_to_left
        self._left_to_right: float = left_to_right
        self._right_to_left: float = right_to_left
        self._right_to_right: float = right_to_right

    @property
    def data(self) -> ChannelMixData:
        return {
            "leftToLeft":   self._left_to_left,
            "leftToRight":  self._left_to_right,
            "rightToLeft":  self._right_to_left,
            "rightToRight": self._right_to_right
        }

    @classmethod
    def mono(cls) -> ChannelMix:
        return cls(left_to_left=0.5, left_to_right=0.5, right_to_left=0.5, right_to_right=0.5)

    @classmethod
    def switch(cls) -> ChannelMix:
        return cls(left_to_left=0.0, left_to_right=1.0, right_to_left=1.0, right_to_right=0.0)

    @classmethod
    def only_left(cls) -> ChannelMix:
        return cls(left_to_left=1.0, left_to_right=0.0, right_to_left=0.0, right_to_right=0.0)

    @classmethod
    def full_left(cls) -> ChannelMix:
        return cls(left_to_left=0.5, left_to_right=0.0, right_to_left=0.5, right_to_right=0.0)

    @classmethod
    def only_right(cls) -> ChannelMix:
        return cls(left_to_left=0.0, left_to_right=0.0, right_to_left=0.0, right_to_right=1.0)

    @classmethod
    def full_right(cls) -> ChannelMix:
        return cls(left_to_left=0.0, left_to_right=0.5, right_to_left=0.0, right_to_right=0.5)


class LowPass(_FilterBase):

    __slots__ = ("_smoothing",)

    def __init__(self, *, smoothing: float = 1.0) -> None:
        if smoothing < 1.0:
            raise ValueError("'smoothing' must be more than or equal to 1.0.")
        self._smoothing: float = smoothing

    @property
    def data(self) -> LowPassData:
        return {"smoothing": self._smoothing}


class Filter(_FilterBase):

    __slots__ = (
        "_filter", "_equalizer", "_karaoke", "_timescale", "_tremolo", "_vibrato", "_rotation", "_distortion",
        "_channel_mix", "_low_pass",
    )

    def __init__(
        self,
        filter: Filter | None = None,
        equalizer: Equalizer | None = None,
        karaoke: Karaoke | None = None,
        timescale: Timescale | None = None,
        tremolo: Tremolo | None = None,
        vibrato: Vibrato | None = None,
        rotation: Rotation | None = None,
        distortion: Distortion | None = None,
        channel_mix: ChannelMix | None = None,
        low_pass: LowPass | None = None,
    ) -> None:
        self._filter: Filter | None = filter
        self._equalizer: Equalizer | None = equalizer
        self._karaoke: Karaoke | None = karaoke
        self._timescale: Timescale | None = timescale
        self._tremolo: Tremolo | None = tremolo
        self._vibrato: Vibrato | None = vibrato
        self._rotation: Rotation | None = rotation
        self._distortion: Distortion | None = distortion
        self._channel_mix: ChannelMix | None = channel_mix
        self._low_pass: LowPass | None = low_pass

    @property
    def data(self) -> FiltersData:

        payload: FiltersData = self._filter.data if self._filter else {}

        if self._equalizer:
            payload["equalizer"] = self._equalizer.data
        if self._karaoke:
            payload["karaoke"] = self._karaoke.data
        if self._timescale:
            payload["timescale"] = self._timescale.data
        if self._tremolo:
            payload["tremolo"] = self._tremolo.data
        if self._vibrato:
            payload["vibrato"] = self._vibrato.data
        if self._rotation:
            payload["rotation"] = self._rotation.data
        if self._distortion:
            payload["distortion"] = self._distortion.data
        if self._channel_mix:
            payload["channelMix"] = self._channel_mix.data
        if self._low_pass:
            payload["lowPass"] = self._low_pass.data

        return payload
