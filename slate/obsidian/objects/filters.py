"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional


__all__ = ['BaseFilter', 'Tremolo', 'Equalizer', 'Distortion', 'Timescale', 'Karaoke', 'ChannelMix', 'Vibrato', 'Rotation', 'LowPass', 'ObsidianFilter']


class BaseFilter(abc.ABC):
    """
    An abstract base class that all filter objects must inherit from.
    """

    def __init__(self) -> None:
        self._name = 'BaseFilter'

    def __repr__(self) -> str:
        return f'slate.BaseFilter name=\'{self.name}\''

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        """
        :py:class:`str`:
            The name of this filter.
        """
        return self._name

    #

    @property
    @abc.abstractmethod
    def _payload(self) -> Any:
        raise NotImplementedError


class Tremolo(BaseFilter):

    def __init__(self, *, frequency: float = 2.0, depth: float = 0.5) -> None:
        super().__init__()

        if frequency < 0:
            raise ValueError('Frequency must be more than 0.0')
        if not 0 < depth <= 1:
            raise ValueError('Depth must be more than 0.0 and less than or equal to 1.0')

        self.frequency: float = frequency
        self.depth: float = depth

        self._name = 'Tremolo'

    def __repr__(self) -> str:
        return f'<slate.Tremolo frequency={self.frequency} depth={self.depth}>'

    #

    @property
    def _payload(self) -> Dict[str, float]:
        return {'frequency': self.frequency, 'depth': self.depth}


class Equalizer(BaseFilter):

    def __init__(self, *, gains: List[float], name: str = 'Equalizer') -> None:
        super().__init__()

        for gain in gains:
            if gain < -0.25 or gain > 1.0:
                raise ValueError('Gain must be within the valid range of -0.25 to 1.0')

        self._gains = gains

        self._name = name

    def __repr__(self) -> str:
        return f'<slate.Equalizer name=\'{self._name}\' gains={self._gains}>'

    #

    @property
    def _payload(self) -> List[float]:
        return self._gains

    #

    @classmethod
    def default(cls) -> Equalizer:
        """
        A factory method that returns an :py:class:`Equalizer` with all bands set to the default gain of 0.
        """

        gains = [0.0] * 15
        return cls(gains=gains, name='Default equalizer')


class Distortion(BaseFilter):

    def __init__(self, *, sin_offset: int = 0, sin_scale: int = 1, cos_offset: int = 0, cos_scale: int = 1, tan_offset: int = 0, tan_scale: int = 1, offset: int = 0, scale: int = 1) -> None:
        super().__init__()

        self.sin_offset: int = sin_offset
        self.sin_scale: int = sin_scale
        self.cos_offset: int = cos_offset
        self.cos_scale: int = cos_scale
        self.tan_offset: int = tan_offset
        self.tan_scale: int = tan_scale
        self.offset: int = offset
        self.scale: int = scale

        self._name = 'Distortion'

    def __repr__(self) -> str:
        return f'''\
        <slate.Distortion sin_offset={self.sin_offset} sin_scale={self.sin_scale} cos_offset={self.cos_offset} cos_scale={self.cos_scale} tan_offset={self.tan_offset} tan_scale={self.tan_scale}\
        offset={self.offset} scale={self.scale}>\
        '''

    #

    @property
    def _payload(self) -> Dict[str, float]:
        return {
            'sinOffset': self.sin_offset, 'sinScale': self.sin_scale, 'cosOffset': self.cos_offset, 'cosScale': self.cos_scale, 'tanOffset': self.tan_offset, 'tanScale': self.tan_scale,
            'offset': self.offset, 'scale': self.scale
        }


class Timescale(BaseFilter):

    def __init__(
            self, *, pitch: float = 1.0, pitch_octaves: Optional[float] = None, pitch_semi_tones: Optional[float] = None, rate: float = 1.0, rate_change: Optional[float] = None, speed: float = 1.0,
            speed_change: Optional[float] = None
    ) -> None:
        super().__init__()

        if (pitch_octaves and pitch) or (pitch_semi_tones and pitch) or (pitch_octaves and pitch_semi_tones):
            raise ValueError('Only one of \'pitch\', \'pitch_octaves\' and \'pitch_semi_tones\' may be set.')
        if rate and rate_change:
            raise ValueError('Only one of \'rate\' and \'rate_change\' may be set.')
        if speed and speed_change:
            raise ValueError('Only one of \'speed\' and \'speed_change\' may be set.')

        self.pitch: float = pitch
        self.pitch_octaves: Optional[float] = pitch_octaves
        self.pitch_semi_tones: Optional[float] = pitch_semi_tones

        self.rate: float = rate
        self.rate_change: Optional[float] = rate_change

        self.speed: float = speed
        self.speed_change: Optional[float] = speed_change

        self._name = 'Timescale'

    def __repr__(self) -> str:
        return f'''\
        <slate.Timescale pitch={self.pitch} pitch_octaves={self.pitch_octaves} pitch_semi_tones={self.pitch_semi_tones} rate={self.rate} rate_change={self.rate_change} speed={self.speed}\
        speed_change={self.speed_change}>\
        '''

    #

    @property
    def _payload(self) -> Dict[str, Optional[float]]:
        return {
            'pitch': self.pitch, 'pitch_octaves': self.pitch_octaves, 'pitch_semi_tones': self.pitch_semi_tones, 'rate': self.rate, 'rate_change': self.rate_change, 'speed': self.speed,
            'speed_change': self.speed_change
        }


class Karaoke(BaseFilter):

    def __init__(self, *, level: float = 1.0, mono_level: float = 1.0, filter_band: float = 220.0, filter_width: float = 100.0) -> None:
        super().__init__()

        self.level: float= level
        self.mono_level: float = mono_level
        self.filter_band: float = filter_band
        self.filter_width: float = filter_width

        self._name = 'Karaoke'

    def __repr__(self) -> str:
        return f'<slate.Karaoke level={self.level} mono_level={self.mono_level} filter_band={self.filter_band} filter_width={self.filter_width}>'

    #

    @property
    def _payload(self) -> Dict[str, float]:
        return {'level': self.level, 'mono_level': self.mono_level, 'filter_band': self.filter_band, 'filter_width': self.filter_width}


class ChannelMix(BaseFilter):

    def __init__(self, *, left_to_left: float = 1, right_to_right: float = 1, left_to_right: float = 0, right_to_left: float = 0) -> None:
        super().__init__()

        if 0 > left_to_left > 1:
            raise ValueError('\'left_to_left\' value must be more than or equal to 0 or less than or equal to 1.')
        if 0 > right_to_right > 1:
            raise ValueError('\'right_to_right\' value must be more than or equal to 0 or less than or equal to 1.')
        if 0 > left_to_right > 1:
            raise ValueError('\'left_to_right\' value must be more than or equal to 0 or less than or equal to 1.')
        if 0 > right_to_left > 1:
            raise ValueError('\'right_to_left\' value must be more than or equal to 0 or less than or equal to 1.')

        self.left_to_left: float = left_to_left
        self.right_to_right: float = right_to_right
        self.left_to_right: float = left_to_right
        self.right_to_left: float = right_to_left

        self._name = 'Channel Mix'

    def __repr__(self) -> str:
        return f'<slate.ChannelMix left_to_left={self.left_to_left} right_to_right{self.right_to_right} left_to_right={self.left_to_right} right_to_left={self.right_to_left}>'

    #

    @property
    def _payload(self) -> Dict[str, float]:
        return {'left_to_left': self.left_to_left, 'right_to_right': self.right_to_right, 'left_to_right': self.left_to_right, 'right_to_left': self.right_to_left}


class Vibrato(BaseFilter):

    def __init__(self, *, frequency: float = 2.0, depth: float = 0.5) -> None:
        super().__init__()

        if not 0 < frequency <= 14:
            raise ValueError('Frequency must be more than 0.0 and less than or equal to 14.0')
        if not 0 < depth <= 1:
            raise ValueError('Depth must be more than 0.0 and less than or equal to 1.0')

        self.frequency: float = frequency
        self.depth: float = depth

        self._name = 'Vibrato'

    def __repr__(self) -> str:
        return f'<slate.Vibrato frequency={self.frequency} depth={self.depth}>'

    #

    @property
    def _payload(self) -> Dict[str, float]:
        return {'frequency': self.frequency, 'depth': self.depth}


class Rotation(BaseFilter):

    def __init__(self, *, rotation_hertz: float = 5) -> None:
        super().__init__()

        self.rotation_hertz: float = rotation_hertz

        self._name = 'Rotation'

    def __repr__(self) -> str:
        return f'<slate.Rotation rotation_hertz={self.rotation_hertz}>'

    #

    @property
    def _payload(self) -> float:
        return self.rotation_hertz


class LowPass(BaseFilter):

    def __init__(self, *, smoothing: float = 20) -> None:
        super().__init__()

        self.smoothing: float = smoothing

        self._name = 'Low Pass'

    def __repr__(self) -> str:
        return f'<slate.LowPass smoothing={self.smoothing}>'

    #

    @property
    def _payload(self) -> float:
        return self.smoothing


class ObsidianFilter:

    def __init__(
            self, filter: Optional[ObsidianFilter] = None, *, volume: Optional[float] = None, tremolo: Optional[Tremolo] = None, equalizer: Optional[Equalizer] = None,
            distortion: Optional[Distortion] = None, timescale: Optional[Timescale] = None, karaoke: Optional[Karaoke] = None, channel_mix: Optional[ChannelMix] = None,
            vibrato: Optional[Vibrato] = None, rotation: Optional[Rotation] = None, low_pass: Optional[LowPass] = None
    ) -> None:

        self.filter: Optional[ObsidianFilter] = filter

        self.volume: Optional[float] = volume
        self.tremolo: Optional[Tremolo] = tremolo
        self.equalizer: Optional[Equalizer] = equalizer
        self.distortion: Optional[Distortion] = distortion
        self.timescale: Optional[Timescale] = timescale
        self.karaoke: Optional[Karaoke] = karaoke
        self.channel_mix: Optional[ChannelMix] = channel_mix
        self.vibrato: Optional[Vibrato] = vibrato
        self.rotation: Optional[Rotation] = rotation
        self.low_pass: Optional[LowPass] = low_pass

    def __repr__(self) -> str:
        return f'<slate.Filter>'

    @property
    def _payload(self):

        payload = self.filter._payload.copy() if self.filter else {}

        if self.volume:
            payload['volume'] = self.volume
        if self.tremolo:
            payload['tremolo'] = self.tremolo._payload
        if self.equalizer:
            payload['equalizer'] = self.equalizer._payload
        if self.distortion:
            payload['distortion'] = self.distortion._payload
        if self.timescale:
            payload['timescale'] = self.timescale._payload
        if self.karaoke:
            payload['karaoke'] = self.karaoke._payload
        if self.channel_mix:
            payload['channel_mix'] = self.channel_mix._payload
        if self.vibrato:
            payload['vibrato'] = self.vibrato._payload
        if self.rotation:
            payload['rotation'] = self.rotation._payload
        if self.low_pass:
            payload['low_pass'] = self.low_pass._payload

        return payload
