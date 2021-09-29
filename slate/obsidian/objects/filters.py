# Future
from __future__ import annotations

# Standard Library
import abc
from typing import Any


__all__ = (
    "ObsidianBaseFilter",
    "ObsidianTremolo",
    "ObsidianEqualizer",
    "ObsidianDistortion",
    "ObsidianTimescale",
    "ObsidianKaraoke",
    "ObsidianChannelMix",
    "ObsidianVibrato",
    "ObsidianRotation",
    "ObsidianLowPass",
    "ObsidianFilter",
)


class ObsidianBaseFilter(abc.ABC):

    def __init__(self, *, name: str = "BaseFilter") -> None:
        self._name: str = name

    def __repr__(self) -> str:
        return f"<slate.BaseFilter name='{self.name}'>"

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    #

    @property
    @abc.abstractmethod
    def _payload(self) -> Any:
        raise NotImplementedError


class ObsidianTremolo(ObsidianBaseFilter):

    def __init__(
        self,
        *,
        frequency: float = 2.0,
        depth: float = 0.5
    ) -> None:

        super().__init__(name="Tremolo")

        if frequency < 0:
            raise ValueError("Frequency must be more than 0.0")
        if not 0 < depth <= 1:
            raise ValueError("Depth must be more than 0.0 and less than or equal to 1.0")

        self.frequency: float = frequency
        self.depth: float = depth

    def __repr__(self) -> str:
        return f"<slate.ObsidianTremolo frequency={self.frequency}, depth={self.depth}>"

    #

    @property
    def _payload(self) -> dict[str, float]:
        return {
            "frequency": self.frequency,
            "depth":     self.depth
        }


class ObsidianEqualizer(ObsidianBaseFilter):

    def __init__(
        self,
        *,
        gains: list[float],
        name: str = "Equalizer"
    ) -> None:

        super().__init__(name=name)

        for gain in gains:
            if gain < -0.25 or gain > 1.0:
                raise ValueError("Gain must be within the valid range of -0.25 to 1.0")

        self._gains = gains

    def __repr__(self) -> str:
        return f"<slate.ObsidianEqualizer name='{self._name}', gains={self._gains}>"

    #

    @property
    def _payload(self) -> list[float]:
        return self._gains

    #

    @classmethod
    def default(cls) -> ObsidianEqualizer:
        gains = [0.0] * 15
        return cls(gains=gains, name="Default equalizer")


class ObsidianDistortion(ObsidianBaseFilter):

    def __init__(
        self,
        *,
        sin_offset: float = 0,
        sin_scale: float = 1,
        cos_offset: float = 0,
        cos_scale: float = 1,
        tan_offset: float = 0,
        tan_scale: float = 1,
        offset: float = 0,
        scale: float = 1
    ) -> None:

        super().__init__(name="Distortion")

        self.sin_offset: float = sin_offset
        self.sin_scale: float = sin_scale
        self.cos_offset: float = cos_offset
        self.cos_scale: float = cos_scale
        self.tan_offset: float = tan_offset
        self.tan_scale: float = tan_scale
        self.offset: float = offset
        self.scale: float = scale

    def __repr__(self) -> str:
        return f"<slate.ObsidianDistortion sin_offset={self.sin_offset}, sin_scale={self.sin_scale}, cos_offset={self.cos_offset}, " \
               f"cos_scale={self.cos_scale}, tan_offset={self.tan_offset}, tan_scale={self.tan_scale}, offset={self.offset}, scale={self.scale}>"

    #

    @property
    def _payload(self) -> dict[str, float]:
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


class ObsidianTimescale(ObsidianBaseFilter):

    def __init__(
        self,
        *,
        pitch: float = 1.0,
        pitch_octaves: float | None = None,
        pitch_semi_tones: float | None = None,
        rate: float = 1.0,
        rate_change: float | None = None,
        speed: float = 1.0,
        speed_change: float | None = None
    ) -> None:

        super().__init__(name="Timescale")

        if (pitch_octaves and pitch) or (pitch_semi_tones and pitch) or (pitch_octaves and pitch_semi_tones):
            raise ValueError("Only one of 'pitch', 'pitch_octaves' and 'pitch_semi_tones' may be set.")
        if rate and rate_change:
            raise ValueError("Only one of 'rate' and 'rate_change' may be set.")
        if speed and speed_change:
            raise ValueError("Only one of 'speed' and 'speed_change' may be set.")

        self.pitch: float = pitch
        self.pitch_octaves: float | None = pitch_octaves
        self.pitch_semi_tones: float | None = pitch_semi_tones

        self.rate: float = rate
        self.rate_change: float | None = rate_change

        self.speed: float = speed
        self.speed_change: float | None = speed_change

    def __repr__(self) -> str:
        return f"<slate.ObsidianTimescale pitch={self.pitch}, pitch_octaves={self.pitch_octaves}, pitch_semi_tones={self.pitch_semi_tones}, " \
               f"rate={self.rate}, rate_change={self.rate_change}, speed={self.speed}, speed_change={self.speed_change}>"

    #

    @property
    def _payload(self) -> dict[str, float | None]:
        return {
            "pitch":            self.pitch,
            "pitch_octaves":    self.pitch_octaves,
            "pitch_semi_tones": self.pitch_semi_tones,
            "rate":             self.rate,
            "rate_change":      self.rate_change,
            "speed":            self.speed,
            "speed_change":     self.speed_change
        }


class ObsidianKaraoke(ObsidianBaseFilter):

    def __init__(
        self,
        *,
        level: float = 1.0,
        mono_level: float = 1.0,
        filter_band: float = 220.0,
        filter_width: float = 100.0
    ) -> None:
        super().__init__(name="Karaoke")

        self.level: float = level
        self.mono_level: float = mono_level
        self.filter_band: float = filter_band
        self.filter_width: float = filter_width

    def __repr__(self) -> str:
        return f"<slate.ObsidianKaraoke level={self.level}, mono_level={self.mono_level}, filter_band={self.filter_band}, filter_width={self.filter_width}>"

    #

    @property
    def _payload(self) -> dict[str, float]:
        return {
            "level":        self.level,
            "mono_level":   self.mono_level,
            "filter_band":  self.filter_band,
            "filter_width": self.filter_width
        }


class ObsidianChannelMix(ObsidianBaseFilter):

    def __init__(
        self,
        *,
        left_to_left: float = 1,
        right_to_right: float = 1,
        left_to_right: float = 0,
        right_to_left: float = 0
    ) -> None:

        super().__init__(name="Channel Mix")

        if 0 > left_to_left > 1:
            raise ValueError("'left_to_left' value must be more than or equal to 0 or less than or equal to 1.")
        if 0 > right_to_right > 1:
            raise ValueError("'right_to_right' value must be more than or equal to 0 or less than or equal to 1.")
        if 0 > left_to_right > 1:
            raise ValueError("'left_to_right' value must be more than or equal to 0 or less than or equal to 1.")
        if 0 > right_to_left > 1:
            raise ValueError("'right_to_left' value must be more than or equal to 0 or less than or equal to 1.")

        self.left_to_left: float = left_to_left
        self.right_to_right: float = right_to_right
        self.left_to_right: float = left_to_right
        self.right_to_left: float = right_to_left

    def __repr__(self) -> str:
        return f"<slate.ObsidianChannelMix left_to_left={self.left_to_left}, right_to_right{self.right_to_right}, left_to_right={self.left_to_right}, " \
               f"right_to_left={self.right_to_left}>"

    #

    @property
    def _payload(self) -> dict[str, float]:
        return {
            "left_to_left":   self.left_to_left,
            "right_to_right": self.right_to_right,
            "left_to_right":  self.left_to_right,
            "right_to_left":  self.right_to_left
        }


class ObsidianVibrato(ObsidianBaseFilter):

    def __init__(
        self,
        *,
        frequency: float = 2.0,
        depth: float = 0.5
    ) -> None:

        super().__init__(name="Vibrato")

        if not 0 < frequency <= 14:
            raise ValueError("Frequency must be more than 0.0 and less than or equal to 14.0")
        if not 0 < depth <= 1:
            raise ValueError("Depth must be more than 0.0 and less than or equal to 1.0")

        self.frequency: float = frequency
        self.depth: float = depth

    def __repr__(self) -> str:
        return f"<slate.ObsidianVibrato frequency={self.frequency}, depth={self.depth}>"

    #

    @property
    def _payload(self) -> dict[str, float]:
        return {
            "frequency": self.frequency,
            "depth":     self.depth
        }


class ObsidianRotation(ObsidianBaseFilter):

    def __init__(
        self,
        *,
        rotation_hertz: float = 5
    ) -> None:
        super().__init__(name="Rotation")

        self.rotation_hertz: float = rotation_hertz

    def __repr__(self) -> str:
        return f"<slate.ObsidianRotation rotation_hertz={self.rotation_hertz}>"

    #

    @property
    def _payload(self) -> float:
        return self.rotation_hertz


class ObsidianLowPass(ObsidianBaseFilter):

    def __init__(
        self,
        *,
        smoothing: float = 20
    ) -> None:
        super().__init__(name="Low Pass")

        self.smoothing: float = smoothing

    def __repr__(self) -> str:
        return f"<slate.ObsidianLowPass smoothing={self.smoothing}>"

    #

    @property
    def _payload(self) -> float:
        return self.smoothing


class ObsidianFilter:

    def __init__(
        self,
        filter: ObsidianFilter | None = None,
        *,
        volume: float | None = None,
        tremolo: ObsidianTremolo | None = None,
        equalizer: ObsidianEqualizer | None = None,
        distortion: ObsidianDistortion | None = None,
        timescale: ObsidianTimescale | None = None,
        karaoke: ObsidianKaraoke | None = None,
        channel_mix: ObsidianChannelMix | None = None,
        vibrato: ObsidianVibrato | None = None,
        rotation: ObsidianRotation | None = None,
        low_pass: ObsidianLowPass | None = None
    ) -> None:

        self.filter: ObsidianFilter | None = filter

        self.volume: float | None = volume
        self.tremolo: ObsidianTremolo | None = tremolo
        self.equalizer: ObsidianEqualizer | None = equalizer
        self.distortion: ObsidianDistortion | None = distortion
        self.timescale: ObsidianTimescale | None = timescale
        self.karaoke: ObsidianKaraoke | None = karaoke
        self.channel_mix: ObsidianChannelMix | None = channel_mix
        self.vibrato: ObsidianVibrato | None = vibrato
        self.rotation: ObsidianRotation | None = rotation
        self.low_pass: ObsidianLowPass | None = low_pass

    def __repr__(self) -> str:
        return f"<slate.ObsidianFilter>"

    #

    @property
    def _payload(self) -> dict[str, Any]:

        payload = self.filter._payload.copy() if self.filter else {}

        if self.volume:
            payload["volume"] = self.volume
        if self.tremolo:
            payload["tremolo"] = self.tremolo._payload
        if self.equalizer:
            payload["equalizer"] = self.equalizer._payload
        if self.distortion:
            payload["distortion"] = self.distortion._payload
        if self.timescale:
            payload["timescale"] = self.timescale._payload
        if self.karaoke:
            payload["karaoke"] = self.karaoke._payload
        if self.channel_mix:
            payload["channel_mix"] = self.channel_mix._payload
        if self.vibrato:
            payload["vibrato"] = self.vibrato._payload
        if self.rotation:
            payload["rotation"] = self.rotation._payload
        if self.low_pass:
            payload["low_pass"] = self.low_pass._payload

        return payload
