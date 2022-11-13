from __future__ import annotations

from typing import TypedDict

from typing_extensions import NotRequired

from .channel_mix import ChannelMix, ChannelMixData
from .distortion import Distortion, DistortionData
from .equalizer import Equalizer, EqualizerData
from .karaoke import Karaoke, KaraokeData
from .low_pass import LowPass, LowPassData
from .rotation import Rotation, RotationData
from .timescale import Timescale, TimescaleData
from .tremolo import Tremolo, TremoloData
from .vibrato import Vibrato, VibratoData
from .volume import Volume, VolumeData


__all__ = (
    "FilterPayload",
    "Filter",
)


class FilterPayload(TypedDict):
    volume: NotRequired[VolumeData]
    equalizer: NotRequired[EqualizerData]
    karaoke: NotRequired[KaraokeData]
    timescale: NotRequired[TimescaleData]
    tremolo: NotRequired[TremoloData]
    vibrato: NotRequired[VibratoData]
    rotation: NotRequired[RotationData]
    distortion: NotRequired[DistortionData]
    channelMix: NotRequired[ChannelMixData]
    lowPass: NotRequired[LowPassData]


class Filter:

    __slots__ = (
        "filter",
        "volume",
        "equalizer",
        "karaoke",
        "timescale",
        "tremolo",
        "vibrato",
        "rotation",
        "distortion",
        "channel_mix",
        "low_pass"
    )

    def __init__(
        self,
        filter: Filter | None = None,
        volume: Volume | None = None,
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

        self.filter: Filter | None = filter
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
        return f"<discord.ext.lava.Filter " \
               f"volume={self.volume}, equalizer={self.equalizer}, karaoke={self.karaoke}, " \
               f"timescale={self.timescale}, tremolo={self.tremolo}, vibrato={self.vibrato}, " \
               f"rotation={self.rotation}, distortion={self.distortion}, channel_mix={self.channel_mix}, " \
               f"low_pass={self.low_pass}"

    def construct_payload(self) -> FilterPayload:

        payload: FilterPayload = self.filter.construct_payload() if self.filter else {}

        if self.volume:
            payload["volume"] = self.volume.construct_payload()
        if self.equalizer:
            payload["equalizer"] = self.equalizer.construct_payload()
        if self.karaoke:
            payload["karaoke"] = self.karaoke.construct_payload()
        if self.timescale:
            payload["timescale"] = self.timescale.construct_payload()
        if self.tremolo:
            payload["tremolo"] = self.tremolo.construct_payload()
        if self.vibrato:
            payload["vibrato"] = self.vibrato.construct_payload()
        if self.rotation:
            payload["rotation"] = self.rotation.construct_payload()
        if self.distortion:
            payload["distortion"] = self.distortion.construct_payload()
        if self.channel_mix:
            payload["channelMix"] = self.channel_mix.construct_payload()
        if self.low_pass:
            payload["lowPass"] = self.low_pass.construct_payload()

        return payload
