from __future__ import annotations

import abc
import collections
from typing import Any, Dict, List, Optional, Tuple, Union

__all__ = ['Equalizer', 'Karaoke', 'Timescale', 'Tremolo', 'Vibrato', 'Rotation', 'LowPass', 'ChannelMix', 'Rotation']


class BaseFilter(abc.ABC):

    def __init__(self) -> None:
        self._name = 'BaseFilter'

    def __str__(self) -> str:
        return self._name

    @abc.abstractmethod
    def __repr__(self) -> str:
        pass

    @abc.abstractmethod
    def payload(self) -> Dict[str, Any]:
        pass

    @property
    def name(self) -> str:
        return self._name


class Equalizer(BaseFilter):

    def __init__(self, *, bands: List[Tuple[int, float]], name='Equalizer') -> None:
        super().__init__()
        self._name = name

        self._bands = self._bands(bands=bands)

    #

    def __repr__(self) -> str:
        return f'<slate.Equalizer name=\'{self._name}\' bands={self._bands}>'

    @property
    def payload(self) -> Dict[str, float]:
        return self._bands

    #

    @staticmethod
    def _bands(*, bands: List[Tuple[int, float]]) -> List[Dict[str, float]]:

        for band, gain in bands:

            if band < 0 or band > 14:
                raise ValueError('Band must be within the valid range of 0 to 14.')
            if gain < -0.25 or gain > 1.0:
                raise ValueError('Gain must be within the valid range of -0.25 to 1.0')

        _dict = collections.defaultdict(int)
        _dict.update(bands)

        return [{'band': band, 'gain': _dict[band]} for band in range(15)]

    #

    @classmethod
    def flat(cls) -> Equalizer:

        bands = [(0, 0.0), (1, 0.0), (2, 0.0), (3, 0.0), (4, 0.0), (5, 0.0), (6, 0.0), (7, 0.0), (8, 0.0), (9, 0.0), (10, 0.0), (11, 0.0), (12, 0.0), (13, 0.0), (14, 0.0)]
        return cls(bands=bands, name='Flat')

    # TODO: More classmethods


class Karaoke(BaseFilter):

    def __init__(self, *, level: Optional[float] = 1.0, mono_level: Optional[float] = 1.0, filter_band: Optional[float] = 220.0, filter_width: Optional[float] = 100.0) -> None:
        super().__init__()

        self.level = level
        self.mono_level = mono_level
        self.filter_band = filter_band
        self.filter_width = filter_width

        self._name = 'Karaoke'

    #

    def __repr__(self) -> str:
        return f'<slate.Karaoke level={self.level} mono_level={self.mono_level} filter_band={self.filter_band} filter_width={self.filter_width}>'

    @property
    def payload(self) -> Dict[str, float]:
        return {'level': self.level, 'mono_level': self.mono_level, 'filter_band': self.filter_band, 'filter_width': self.filter_width}


class Timescale(BaseFilter):

    def __init__(self, *, speed: Optional[float] = 1.0, pitch: Optional[float] = 1.0, rate: Optional[float] = 1.0) -> None:
        super().__init__()

        self.speed = speed
        self.pitch = pitch
        self.rate = rate

        self._name = 'Timescale'

    #

    def __repr__(self) -> str:
        return f'<slate.Timescale speed={self.speed} pitch={self.pitch} rate={self.rate}>'

    @property
    def payload(self) -> Dict[str, float]:
        return {'speed': self.speed, 'pitch': self.pitch, 'rate': self.rate}


class Tremolo(BaseFilter):

    def __init__(self, *, frequency: Optional[float] = 2.0, depth: Optional[float] = 0.5) -> None:
        super().__init__()

        if frequency < 0:
            raise ValueError('Frequency must be more than 0.0')
        if not 0 < depth <= 1:
            raise ValueError('Depth must be more than 0.0 and less than or equal to 1.0')

        self.frequency = frequency
        self.depth = depth

        self._name = 'Tremolo'

    #

    def __repr__(self) -> str:
        return f'<slate.Tremolo frequency={self.frequency} depth={self.depth}>'

    @property
    def payload(self) -> Dict[str, float]:
        return {'frequency': self.frequency, 'depth': self.depth}


class Vibrato(BaseFilter):

    def __init__(self, *, frequency: Optional[float] = 2.0, depth: Optional[float] = 0.5) -> None:
        super().__init__()

        if not 0 < frequency <= 14:
            raise ValueError('Frequency must be more than 0.0 and less than or equal to 14.0')
        if not 0 < depth <= 1:
            raise ValueError('Depth must be more than 0.0 and less than or equal to 1.0')

        self.frequency = frequency
        self.depth = depth

        self._name = 'Vibrato'

    #

    def __repr__(self) -> str:
        return f'<slate.Vibrato frequency={self.frequency} depth={self.depth}>'

    @property
    def payload(self) -> Dict[str, float]:
        return {'frequency': self.frequency, 'depth': self.depth}


class Rotation(BaseFilter):

    def __init__(self, *, rotation_hz: Optional[float] = 5) -> None:
        super().__init__()

        self.rotation_hz = rotation_hz

        self._name = 'Rotation'

    #

    def __repr__(self) -> str:
        return f'<slate.Rotation rotation_hz={self.rotation_hz}>'

    @property
    def payload(self) -> Dict[str, float]:
        return {'rotationHz': self.rotation_hz}


class LowPass(BaseFilter):

    def __init__(self, *, smoothing: Optional[float] = 20) -> None:
        super().__init__()

        self.smoothing = smoothing

        self._name = 'Low Pass'

    #

    def __repr__(self) -> str:
        return f'<slate.LowPass smoothing={self.smoothing}>'

    @property
    def payload(self) -> Dict[str, float]:
        return {'smoothing': self.smoothing}


class ChannelMix(BaseFilter):

    def __init__(
            self, *, left_to_left: Optional[bool] = True, right_to_right: Optional[bool] = True, left_to_right: Optional[bool] = False, right_to_left: Optional[bool] = False
    ) -> None:
        super().__init__()

        self.left_to_left = left_to_left
        self.right_to_right = right_to_right
        self.left_to_right = left_to_right
        self.right_to_left = right_to_left

        self._name = 'Channel Mix'

    #

    def __repr__(self) -> str:
        return f'<slate.ChannelMix left_to_left={self.left_to_left} right_to_right{self.right_to_right} left_to_right={self.left_to_right} right_to_left={self.right_to_left}>'

    @property
    def payload(self) -> Dict[str, float]:
        return {'left_to_left': self.left_to_left, 'right_to_right': self.right_to_right, 'left_to_right': self.left_to_right, 'right_to_left': self.right_to_left}


class Filter:

    def __init__(
            self, *, filter: Filter = None, volume: Optional[float] = None, equalizer: Optional[Equalizer] = None, karaoke: Optional[Karaoke] = None,
            timescale: Optional[Timescale] = None, tremolo: Optional[Tremolo] = None, vibrato: Optional[Vibrato] = None, rotation: Optional[Rotation] = None,
            low_pass: Optional[LowPass] = None, channel_mix: Optional[ChannelMix] = None
    ) -> None:

        self.filter = filter
        self.volume = volume
        self.equalizer = equalizer
        self.karaoke = karaoke
        self.timescale = timescale
        self.tremolo = tremolo
        self.vibrato = vibrato
        self.rotation = rotation
        self.low_pass = low_pass
        self.channel_mix = channel_mix

    def __repr__(self) -> str:
        return f'<slate.Filter volume={self.volume} equalizer={self.equalizer} karaoke={self.karaoke} timescale={self.timescale} tremolo={self.tremolo} vibrato={self.vibrato} ' \
               f'rotation={self.rotation} low_pass={self.low_pass} channel_mix={self.channel_mix}>'

    @property
    def payload(self) -> Dict[str, Union[Dict[str, float], float]]:

        payload = self.filter.payload.copy() if self.filter is not None else {}

        if self.volume is not None:
            payload['volume'] = self.volume

        if self.equalizer:
            payload['equalizer'] = self.equalizer.payload
        if self.karaoke:
            payload['karaoke'] = self.karaoke.payload
        if self.timescale:
            payload['timescale'] = self.timescale.payload
        if self.tremolo:
            payload['tremolo'] = self.tremolo.payload
        if self.vibrato:
            payload['vibrato'] = self.vibrato.payload
        if self.rotation:
            payload['rotation'] = self.rotation.payload
        if self.low_pass:
            payload['lowpass'] = self.low_pass.payload
        if self.channel_mix:
            payload['channelmix'] = self.channel_mix.payload

        return payload
