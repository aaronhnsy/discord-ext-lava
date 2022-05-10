# Future
from __future__ import annotations

# Standard Library
import collections


__all__ = (
    "Volume",
    "Tremolo",
    "Equalizer",
    "Distortion",
    "Timescale",
    "Karaoke",
    "ChannelMix",
    "Vibrato",
    "Rotation",
    "LowPass",
    "Filter",
)


class Volume:

    def __init__(self, *, level: float = 100.0) -> None:

        if level < 0.0 or level > 500.0:
            raise ValueError("'level' must be more than or equal to 0.0 and less than or equal to 500.0.")

        self.level: float = level

    def __repr__(self) -> str:
        return f"<slate.Volume level={self.level}>"

    @property
    def payload(self) -> float:
        return self.level / 100.0


class Tremolo:

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
        return f"<slate.Tremolo frequency={self.frequency}, depth={self.depth}>"

    @property
    def payload(self) -> dict[str, float]:
        return {
            "frequency": self.frequency,
            "depth":     self.depth
        }


class Equalizer:

    def __init__(
        self,
        *,
        name: str = "CustomEqualizer",
        bands: list[tuple[int, float]]
    ) -> None:

        if any((band, gain) for band, gain in bands if band < 0 or band > 15 or gain < -0.25 or gain > 1.0):
            raise ValueError("Equalizer bands must be between 0 and 15 and gains must be between -0.25 and 1.0.")

        _dict: collections.defaultdict[float, float] = collections.defaultdict(float)
        _dict.update(bands)

        self.name: str = name
        self.bands: list[dict[str, int | float]] = [{"band": band, "gain": _dict[band]} for band in range(15)]

    def __repr__(self) -> str:
        return f"<slate.Equalizer name='{self.name}', bands={self.bands}>"

    @property
    def payload(self) -> list[dict[str, int | float]]:
        return self.bands


class Distortion:

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
        return f"<slate.Distortion " \
               f"sin_offset={self.sin_offset}, sin_scale={self.sin_scale}, " \
               f"cos_offset={self.cos_offset}, cos_scale={self.cos_scale}, " \
               f"tan_offset={self.tan_offset}, tan_scale={self.tan_scale}, " \
               f"offset={self.offset}, scale={self.scale}>"

    @property
    def payload(self) -> dict[str, float]:
        return {
            "sin_offset": self.sin_offset,
            "sin_scale":  self.sin_scale,
            "cos_offset": self.cos_offset,
            "cos_scale":  self.cos_scale,
            "tan_offset": self.tan_offset,
            "tan_scale":  self.tan_scale,
            "offset":     self.offset,
            "scale":      self.scale
        }


class Timescale:

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

    @property
    def payload(self) -> dict[str, float]:
        return {
            "pitch": self.pitch,
            "speed": self.speed,
            "rate":  self.rate,
        }


class Karaoke:

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

    @property
    def payload(self) -> dict[str, float]:
        return {
            "level":        self.level,
            "mono_level":   self.mono_level,
            "filter_band":  self.band,
            "filter_width": self.band_width
        }


class ChannelMix:

    def __init__(
        self,
        *,
        left_to_left: float = 1.0,
        left_to_right: float = 0.0,
        right_to_left: float = 0.0,
        right_to_right: float = 1.0,
    ) -> None:

        _all = (left_to_left, left_to_right, right_to_left, right_to_right)

        if any(value for value in _all if value < 0.0 or value > 1.0):
            raise ValueError(
                "'left_to_left', 'left_to_right', 'right_to_left', and 'right_to_right' must all be between "
                "(or equal to) 0.0 and 1.0."
            )

        self.left_to_left: float = left_to_left
        self.right_to_right: float = right_to_right
        self.left_to_right: float = left_to_right
        self.right_to_left: float = right_to_left

    def __repr__(self) -> str:
        return f"<slate.ChannelMix " \
               f"left_to_left={self.left_to_left}, right_to_right{self.right_to_right}, " \
               f"left_to_right={self.left_to_right}, right_to_left={self.right_to_left}>"

    @property
    def payload(self) -> dict[str, float]:
        return {
            "left_to_left":   self.left_to_left,
            "left_to_right":  self.left_to_right,
            "right_to_left":  self.right_to_left,
            "right_to_right": self.right_to_right,
        }

    @classmethod
    def mono(cls) -> ChannelMix:
        return cls(left_to_left=0.5, left_to_right=0.5, right_to_left=0.5, right_to_right=0.5)

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

    @classmethod
    def switch(cls) -> ChannelMix:
        return cls(left_to_left=0.0, left_to_right=1.0, right_to_left=1.0, right_to_right=0.0)


class Vibrato:

    def __init__(
        self,
        *,
        frequency: float = 2.0,
        depth: float = 0.5
    ) -> None:

        if frequency <= 0.0 or frequency > 14.0:
            raise ValueError("'frequency' must be more than 0.0 and less than or equal to 14.0.")
        if depth <= 0.0 or depth > 1.0:
            raise ValueError("'depth' must be more than 0.0 and less than or equal to 1.0.")

        self.frequency: float = frequency
        self.depth: float = depth

    def __repr__(self) -> str:
        return f"<slate.Vibrato frequency={self.frequency}, depth={self.depth}>"

    @property
    def payload(self) -> dict[str, float]:
        return {
            "frequency": self.frequency,
            "depth":     self.depth
        }


class Rotation:

    def __init__(
        self,
        *,
        speed: float = 5.0
    ) -> None:
        self.speed: float = speed

    def __repr__(self) -> str:
        return f"<slate.Rotation speed={self.speed}>"

    @property
    def payload(self) -> float:
        return self.speed


class LowPass:

    def __init__(
        self,
        *,
        smoothing: float = 20.0
    ) -> None:
        self.smoothing: float = smoothing

    def __repr__(self) -> str:
        return f"<slate.LowPass smoothing={self.smoothing}>"

    @property
    def payload(self) -> float:
        return self.smoothing


class Filter:

    def __init__(
        self,
        _filter: Filter | None = None, /,
        *,
        volume: Volume | None = None,
        tremolo: Tremolo | None = None,
        equalizer: Equalizer | None = None,
        distortion: Distortion | None = None,
        timescale: Timescale | None = None,
        karaoke: Karaoke | None = None,
        channel_mix: ChannelMix | None = None,
        vibrato: Vibrato | None = None,
        rotation: Rotation | None = None,
        low_pass: LowPass | None = None
    ) -> None:

        self.filter: Filter | None = _filter

        self.volume: Volume | None = volume
        self.equalizer: Equalizer | None = equalizer
        self.karaoke: Karaoke | None = karaoke
        self.timescale: Timescale | None = timescale
        self.tremolo: Tremolo | None = tremolo
        self.vibrato: Vibrato | None = vibrato
        self.rotation: Rotation | None = rotation
        self.distortion: Distortion | None = distortion
        self.channel_mix: ChannelMix | None = channel_mix
        self.low_pass: LowPass | None = low_pass

    def __repr__(self) -> str:
        return f"<slate.Filter " \
               f"volume={self.volume}, tremolo={self.tremolo}, equalizer={self.equalizer}, " \
               f"distortion={self.distortion}, timescale={self.timescale}, karaoke={self.karaoke}, " \
               f"channel_mix={self.channel_mix}, vibrato={self.vibrato}, rotation={self.rotation}, " \
               f"low_pass={self.low_pass}>"

    @property
    def payload(self) -> dict[str, dict[str, float] | list[dict[str, int | float]] | float]:

        payload = self.filter.payload.copy() if self.filter else {}

        if self.volume:
            payload["volume"] = self.volume.payload
        if self.tremolo:
            payload["tremolo"] = self.tremolo.payload
        if self.equalizer:
            payload["equalizer"] = self.equalizer.payload
        if self.distortion:
            payload["distortion"] = self.distortion.payload
        if self.timescale:
            payload["timescale"] = self.timescale.payload
        if self.karaoke:
            payload["karaoke"] = self.karaoke.payload
        if self.channel_mix:
            payload["channel_mix"] = self.channel_mix.payload
        if self.vibrato:
            payload["vibrato"] = self.vibrato.payload
        if self.rotation:
            payload["rotation"] = self.rotation.payload
        if self.low_pass:
            payload["low_pass"] = self.low_pass.payload

        return payload
