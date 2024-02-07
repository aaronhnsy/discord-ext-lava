from typing import NotRequired, TypedDict


class EqualizerBandData(TypedDict):
    band: int
    gain: float


EqualizerData = list[EqualizerBandData]


class KaraokeData(TypedDict):
    level: NotRequired[float]
    monoLevel: NotRequired[float]
    filterBand: NotRequired[float]
    filterWidth: NotRequired[float]


class TimescaleData(TypedDict):
    pitch: NotRequired[float]
    speed: NotRequired[float]
    rate: NotRequired[float]


class TremoloData(TypedDict):
    frequency: NotRequired[float]
    depth: NotRequired[float]


class VibratoData(TypedDict):
    frequency: NotRequired[float]
    depth: NotRequired[float]


class RotationData(TypedDict):
    rotationHz: NotRequired[float]


class DistortionData(TypedDict):
    sinOffset: NotRequired[float]
    sinScale: NotRequired[float]
    cosOffset: NotRequired[float]
    cosScale: NotRequired[float]
    tanOffset: NotRequired[float]
    tanScale: NotRequired[float]
    offset: NotRequired[float]
    scale: NotRequired[float]


class ChannelMixData(TypedDict):
    leftToLeft: NotRequired[float]
    leftToRight: NotRequired[float]
    rightToLeft: NotRequired[float]
    rightToRight: NotRequired[float]


class LowPassData(TypedDict):
    smoothing: NotRequired[float]


class FiltersData(TypedDict):
    equalizer: NotRequired[EqualizerData]
    karaoke: NotRequired[KaraokeData]
    timescale: NotRequired[TimescaleData]
    tremolo: NotRequired[TremoloData]
    vibrato: NotRequired[VibratoData]
    rotation: NotRequired[RotationData]
    distortion: NotRequired[DistortionData]
    channelMix: NotRequired[ChannelMixData]
    lowPass: NotRequired[LowPassData]
