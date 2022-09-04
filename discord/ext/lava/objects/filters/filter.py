from __future__ import annotations

from typing import TypedDict

from ..enums import Provider
from .channel_mix import ChannelMix, LavalinkChannelMixData, ObsidianChannelMixData
from .distortion import Distortion, LavalinkDistortionData, ObsidianDistortionData
from .equalizer import Equalizer, EqualizerData
from .karaoke import Karaoke, LavalinkKaraokeData, ObsidianKaraokeData
from .low_pass import LavalinkLowPassData, LowPass, ObsidianLowPassData
from .rotation import LavalinkRotationData, ObsidianRotationData, Rotation
from .timescale import Timescale, TimescaleData
from .tremolo import Tremolo, TremoloData
from .vibrato import Vibrato, VibratoData
from .volume import Volume, VolumeData


__all__ = (
    "ObsidianFilterPayload",
    "LavalinkFilterPayload",
    "Filter",
)


class ObsidianFilterPayload(TypedDict, total=False):
    channel_mix: ObsidianChannelMixData
    distortion: ObsidianDistortionData
    equalizer: EqualizerData
    karaoke: ObsidianKaraokeData
    low_pass: ObsidianLowPassData
    rotation: ObsidianRotationData
    timescale: TimescaleData
    tremolo: TremoloData
    vibrato: VibratoData
    volume: VolumeData


class LavalinkFilterPayload(TypedDict, total=False):
    channelMix: LavalinkChannelMixData
    distortion: LavalinkDistortionData
    equalizer: EqualizerData
    karaoke: LavalinkKaraokeData
    lowPass: LavalinkLowPassData
    rotation: LavalinkRotationData
    timescale: TimescaleData
    tremolo: TremoloData
    vibrato: VibratoData
    volume: VolumeData


class Filter:

    __slots__ = (
        "filter",
        "channel_mix",
        "distortion",
        "equalizer",
        "karaoke",
        "low_pass",
        "rotation",
        "timescale",
        "tremolo",
        "vibrato",
        "volume",
    )

    def __init__(
        self,
        filter: Filter | None = None,
        channel_mix: ChannelMix | None = None,
        distortion: Distortion | None = None,
        equalizer: Equalizer | None = None,
        karaoke: Karaoke | None = None,
        low_pass: LowPass | None = None,
        rotation: Rotation | None = None,
        timescale: Timescale | None = None,
        tremolo: Tremolo | None = None,
        vibrato: Vibrato | None = None,
        volume: Volume | None = None,
    ) -> None:

        self.filter: Filter | None = filter
        self.channel_mix: ChannelMix | None = channel_mix
        self.distortion: Distortion | None = distortion
        self.equalizer: Equalizer | None = equalizer
        self.karaoke: Karaoke | None = karaoke
        self.low_pass: LowPass | None = low_pass
        self.rotation: Rotation | None = rotation
        self.timescale: Timescale | None = timescale
        self.tremolo: Tremolo | None = tremolo
        self.vibrato: Vibrato | None = vibrato
        self.volume: Volume | None = volume

    def __repr__(self) -> str:
        return f"<discord.ext.lava.Filter channel_mix={self.channel_mix}, distortion={self.distortion}, " \
               f"equalizer={self.equalizer}, karaoke={self.karaoke}, low_pass={self.low_pass}, " \
               f"rotation={self.rotation}, timescale={self.timescale}, tremolo={self.tremolo}, " \
               f"vibrato={self.vibrato}, volume={self.volume}>"

    # payload

    def _construct_obsidian_payload(self) -> ObsidianFilterPayload:

        payload: ObsidianFilterPayload = self.filter._construct_payload(
            Provider.Obsidian
        ) if self.filter else {}  # type: ignore

        if self.channel_mix:
            payload["channel_mix"] = self.channel_mix._construct_obsidian_payload()
        if self.low_pass:
            payload["low_pass"] = self.low_pass._construct_obsidian_payload()
        if self.distortion:
            payload["distortion"] = self.distortion._construct_obsidian_payload()
        if self.karaoke:
            payload["karaoke"] = self.karaoke._construct_obsidian_payload()
        if self.rotation:
            payload["rotation"] = self.rotation._construct_obsidian_payload()

        return payload

    def _construct_lavalink_payload(self) -> LavalinkFilterPayload:

        payload: LavalinkFilterPayload = self.filter._construct_payload(
            Provider.Lavalink
        ) if self.filter else {}  # type: ignore

        if self.channel_mix:
            payload["channelMix"] = self.channel_mix._construct_lavalink_payload()
        if self.low_pass:
            payload["lowPass"] = self.low_pass._construct_lavalink_payload()
        if self.distortion:
            payload["distortion"] = self.distortion._construct_lavalink_payload()
        if self.karaoke:
            payload["karaoke"] = self.karaoke._construct_lavalink_payload()
        if self.rotation:
            payload["rotation"] = self.rotation._construct_lavalink_payload()

        return payload

    def _construct_payload(self, provider: Provider) -> ObsidianFilterPayload | LavalinkFilterPayload:

        if provider is Provider.Obsidian:
            payload = self._construct_obsidian_payload()
        else:
            payload = self._construct_lavalink_payload()

        if self.equalizer:
            payload["equalizer"] = self.equalizer._construct_payload()
        if self.timescale:
            payload["timescale"] = self.timescale._construct_payload()
        if self.tremolo:
            payload["tremolo"] = self.tremolo._construct_payload()
        if self.vibrato:
            payload["vibrato"] = self.vibrato._construct_payload()
        if self.volume:
            payload["volume"] = self.volume._construct_payload()

        return payload
