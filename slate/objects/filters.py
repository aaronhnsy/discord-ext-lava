from __future__ import annotations

import abc
import collections
from typing import Any, Dict, List, Optional, Tuple, Type

__all__ = ['BaseFilter', 'Equalizer', 'Karaoke', 'Timescale', 'Tremolo', 'Vibrato', 'Rotation', 'LowPass', 'ChannelMix', 'Distortion', 'Filter']


class BaseFilter(abc.ABC):
    """
    An abstract base class that all filter objects must inherit from.
    """

    def __init__(self) -> None:
        self._name = 'BaseFilter'

    def __repr__(self) -> str:
        pass

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
    def _payload(self) -> Dict[str, Dict[str, Any]]:
        pass


class Equalizer(BaseFilter):
    """
    An equalizer filter. There are 15 bands (0-14) that can be changed with values ranging from -0.25 to 1.0. The default value is 0.

    .. note::
        A value of -0.25 means the band is completely muted, while a value of 0.25 means it is doubled.

    Parameters
    ----------
    bands : List [tuple[int, float]
        A list of tuples of each band and it's gain.
    name: str
        A custom name for the equalizer filter.
    """

    def __init__(self, *, bands: List[Tuple[int, float]], name='Equalizer') -> None:
        super().__init__()
        self._name = name

        self._bands = self._bands_generator(bands=bands)

    def __repr__(self) -> str:
        return f'<slate.Equalizer name=\'{self._name}\' bands={self._bands}>'

    #

    @property
    def _payload(self) -> Dict[str, List[Dict[str, float]]]:
        return {'equalizer': self._bands}

    #

    @staticmethod
    def _bands_generator(*, bands: List[Tuple[int, float]]) -> List[Dict[str, float]]:

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
    def default(cls) -> Equalizer:
        """
        A factory method that returns an :py:class:`Equalizer` with all bands set to the default gain of 0.
        """

        bands = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0)]
        return cls(bands=bands, name='Default equalizer')


class Karaoke(BaseFilter):
    """
    A karaoke filter. This uses equalization to eliminate a specific band which usually targets the vocals of a song.

    Parameters
    ----------
    level : Optional[float]
        ...
    mono_level : Optional[float]
        ...
    filter_band : Optional[float]
        ...
    filter_width : Optional[float]
        ...
    """

    def __init__(self, *, level: Optional[float] = 1.0, mono_level: Optional[float] = 1.0, filter_band: Optional[float] = 220.0, filter_width: Optional[float] = 100.0) -> None:
        super().__init__()

        self.level: Optional[float] = level
        self.mono_level: Optional[float] = mono_level
        self.filter_band: Optional[float] = filter_band
        self.filter_width: Optional[float] = filter_width

        self._name = 'Karaoke'

    def __repr__(self) -> str:
        return f'<slate.Karaoke level={self.level} mono_level={self.mono_level} filter_band={self.filter_band} filter_width={self.filter_width}>'

    #

    @property
    def _payload(self) -> Dict[str, Dict[str, float]]:
        return {'karaoke': {'level': self.level, 'mono_level': self.mono_level, 'filter_band': self.filter_band, 'filter_width': self.filter_width}}


class Timescale(BaseFilter):
    """
    A timescale filter, allows you to modify the pitch or speed of a song, or both (rate).

    Parameters
    ----------
    speed : Optional[float]
        The speed of the filter, default value is 1. (Normal speed)
    pitch : Optional[float]
        The pitch of the filter, default value is 1. (Normal pitch)
    rate : Optional[float]
        The speed and pitch of the song, default value is 1. (Normal speed and pitch)
    """

    def __init__(self, *, speed: Optional[float] = 1.0, pitch: Optional[float] = 1.0, rate: Optional[float] = 1.0) -> None:
        super().__init__()

        self.speed: Optional[float]  = speed
        self.pitch: Optional[float]  = pitch
        self.rate: Optional[float]  = rate

        self._name = 'Timescale'

    def __repr__(self) -> str:
        return f'<slate.Timescale speed={self.speed} pitch={self.pitch} rate={self.rate}>'

    #

    @property
    def _payload(self) -> Dict[str, Dict[str, float]]:
        return {'timescale': {'speed': self.speed, 'pitch': self.pitch, 'rate': self.rate}}


class Tremolo(BaseFilter):
    """
    A tremolo filter, this uses amplification to create a shuddering or trembling effect in which the volume oscillates.

    Parameters
    ----------
    frequency : Optional[float]
        The frequency at which the volume will oscillate. Default value is 2, and must always be more than 0.
    depth : Optional[float]
        The factor by which the volume will oscillate. Default value is 0.5, and must always be more than 0 or less than or equal to 1.
    """

    def __init__(self, *, frequency: Optional[float] = 2.0, depth: Optional[float] = 0.5) -> None:
        super().__init__()

        if frequency < 0:
            raise ValueError('Frequency must be more than 0.0')
        if not 0 < depth <= 1:
            raise ValueError('Depth must be more than 0.0 and less than or equal to 1.0')

        self.frequency: Optional[float] = frequency
        self.depth: Optional[float] = depth

        self._name = 'Tremolo'

    def __repr__(self) -> str:
        return f'<slate.Tremolo frequency={self.frequency} depth={self.depth}>'

    #

    @property
    def _payload(self) -> Dict[str, Dict[str, float]]:
        return {'tremolo': {'frequency': self.frequency, 'depth': self.depth}}


class Vibrato(BaseFilter):
    """
    A vibrato filter, this is similar to tremolo in the sense that this oscillates the pitch instead of the volume.

    Parameters
    ----------
    frequency : Optional[float]
        The frequency at which the pitch will oscillate. Default value is 2, and must always be more than 0 or less than or equal to 14.
    depth : Optional[float]
        The factor by which the pitch will oscillate. Default value is 0.5, and must always be more than 0 or less than or equal to 1.
    """

    def __init__(self, *, frequency: Optional[float] = 2.0, depth: Optional[float] = 0.5) -> None:
        super().__init__()

        if not 0 < frequency <= 14:
            raise ValueError('Frequency must be more than 0.0 and less than or equal to 14.0')
        if not 0 < depth <= 1:
            raise ValueError('Depth must be more than 0.0 and less than or equal to 1.0')

        self.frequency: Optional[float] = frequency
        self.depth: Optional[float] = depth

        self._name = 'Vibrato'

    def __repr__(self) -> str:
        return f'<slate.Vibrato frequency={self.frequency} depth={self.depth}>'

    #

    @property
    def _payload(self) -> Dict[str, Dict[str, float]]:
        return {'vibrato': {'frequency': self.frequency, 'depth': self.depth}}


class Rotation(BaseFilter):
    """
    A rotation filter. Rotates the audio around stereo audio channels to create an audio panning effect.

    Parameters
    ----------
    rotation_hertz : Optional[float]
        The frequency of the audio rotating. Default value is 5, recommended value range is 0 - 2.
    """

    def __init__(self, *, rotation_hertz: Optional[float] = 5) -> None:
        super().__init__()

        self.rotation_hertz: Optional[float] = rotation_hertz

        self._name = 'Rotation'

    def __repr__(self) -> str:
        return f'<slate.Rotation rotation_hertz={self.rotation_hertz}>'

    #

    @property
    def _payload(self) -> Dict[str, Dict[str, float]]:
        return {'rotation': {'rotationHz': self.rotation_hertz}}


class LowPass(BaseFilter):
    """
    A low pass filter in which higher frequencies get suppressed while lower ones are allowed to pass through.

    Parameters
    ----------
    smoothing : Optional[float]
        ...
    """

    def __init__(self, *, smoothing: Optional[float] = 20) -> None:
        super().__init__()

        self.smoothing: Optional[float] = smoothing

        self._name = 'Low Pass'

    def __repr__(self) -> str:
        return f'<slate.LowPass smoothing={self.smoothing}>'

    #

    @property
    def _payload(self) -> Dict[str, Dict[str, float]]:
        return {'lowpass': {'smoothing': self.smoothing}}


class ChannelMix(BaseFilter):
    """
    A channel mix filter that allows you to mix left and right audio channels with a configurable factor on how much each one affects the the other. By default both channels are kept separate from eachother, while a value of 0.5 on each factor means both channels get the same audio.

    .. note::
        All values must be more than or equal to 0, or less than or equal to 1.

    Parameters
    ----------
    left_to_left: Optional[float]
        How much of an effect the left channel has an effect on the left channel. Default value is 1.
    right_to_right: Optional[float]
        How much of an effect the right channel has an effect on the right channel. Default value is 1.
    left_to_right: Optional[float]
        How much of an effect the left channel has an effect on the right channel. Default value is 0.
    right_to_left: Optional[float]
        How much of an effect the right channel has an effect on the left channel. Default value is 0.
    """

    def __init__(self, *, left_to_left: Optional[float] = 1, right_to_right: Optional[float] = 1, left_to_right: Optional[float] = 0, right_to_left: Optional[float] = 0) -> None:
        super().__init__()

        if 0 > left_to_left > 1:
            raise ValueError('\'left_to_left\' value must be more than or equal to 0 or less than or equal to 1.')
        if 0 > right_to_right > 1:
            raise ValueError('\'right_to_right\' value must be more than or equal to 0 or less than or equal to 1.')
        if 0 > left_to_right > 1:
            raise ValueError('\'left_to_right\' value must be more than or equal to 0 or less than or equal to 1.')
        if 0 > right_to_left > 1:
            raise ValueError('\'right_to_left\' value must be more than or equal to 0 or less than or equal to 1.')

        self.left_to_left: Optional[float] = left_to_left
        self.right_to_right: Optional[float] = right_to_right
        self.left_to_right: Optional[float] = left_to_right
        self.right_to_left: Optional[float] = right_to_left

        self._name = 'Channel Mix'

    def __repr__(self) -> str:
        return f'<slate.ChannelMix left_to_left={self.left_to_left} right_to_right{self.right_to_right} left_to_right={self.left_to_right} right_to_left={self.right_to_left}>'

    #

    @property
    def _payload(self) -> Dict[str, Dict[str, float]]:
        return {'channelmix': {'left_to_left': self.left_to_left, 'right_to_right': self.right_to_right, 'left_to_right': self.left_to_right, 'right_to_left': self.right_to_left}}


class Distortion(BaseFilter):
    """
    A distortion filter. Can create some pretty cool sound effects.

    Parameters
    ----------
    sin_offset : Optional[int]
        ...
    sin_scale : Optional[int]
        ...
    cos_offset : Optional[int]
        ...
    cos_scale : Optional[int]
        ...
    tan_offset : Optional[int]
        ...
    tan_scale : Optional[int]
        ...
    offset : Optional[int]
        ...
    scale : Optional[int]
        ...
    """

    def __init__(self, *, sin_offset: Optional[int] = 0, sin_scale: Optional[int] = 1, cos_offset: Optional[int] = 0, cos_scale: Optional[int] = 1, tan_offset: Optional[int] = 0,
                 tan_scale: Optional[int] = 1, offset: Optional[int] = 0, scale: Optional[int] = 1) -> None:
        super().__init__()

        self.sin_offset: Optional[int] = sin_offset
        self.sin_scale: Optional[int] = sin_scale
        self.cos_offset: Optional[int] = cos_offset
        self.cos_scale: Optional[int] = cos_scale
        self.tan_offset: Optional[int] = tan_offset
        self.tan_scale: Optional[int] = tan_scale
        self.offset: Optional[int] = offset
        self.scale: Optional[int] = scale

        self._name = 'Distortion'

    def __repr__(self) -> str:
        return f'<slate.Distortion sin_offset={self.sin_offset} sin_scale={self.sin_scale} cos_offset={self.cos_offset} cos_scale={self.cos_scale} tan_offset={self.tan_offset} ' \
               f'tan_scale={self.tan_scale} offset={self.offset} scale={self.scale}>'

    #

    @property
    def _payload(self) -> Dict[str, Dict[str, float]]:
        return {
            'distortion': {
                'sinOffset': self.sin_offset, 'sinScale': self.sin_scale, 'cosOffset': self.cos_offset, 'cosScale': self.cos_scale, 'tanOffset': self.tan_offset,
                'tanScale': self.tan_scale, 'offset': self.offset, 'scale': self.scale
            }
        }


class Filter:
    """
    The main filter classed used to apply filters on a player.

    Parameters
    ----------
    filters : List [ :py:class:`BaseFilter` ]
        A list of instances of subclasses of :py:class:`BaseFilter` that you want to add to this filter.
    filter : Optional[ :py:class:`Filter` ]
        An optional Filter instance that allows you to overwrite the settings of certain filters while retaining old ones.
    volume : Optional[float]
        Optional volume filter. Not recommend for use as :py:meth:`Player.set_volume` works just as well.

    """

    def __init__(self, filters: List[Type[BaseFilter]], *, filter: Filter = None, volume: Optional[float] = None) -> None:

        self.filters: List[Type[BaseFilter]] = filters
        self.filter: Optional[BaseFilter] = filter
        self.volume: Optional[float] = volume

        for filter in self.filters:
            if not issubclass(type(filter), BaseFilter):
                raise ValueError('Arguments passed to this Filter must be subclasses of \'slate.BaseFilter\'.')

    def __repr__(self) -> str:
        return f'<slate.Filter filters={self.filters}, volume={self.volume}>'

    @property
    def _payload(self):

        payload = self.filter._payload.copy() if self.filter is not None else {}

        if self.volume is not None:
            payload['volume'] = self.volume

        for filter in self.filters:
            payload.update(filter._payload)

        return payload
