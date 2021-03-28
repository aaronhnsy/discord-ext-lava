from typing import List

__all__ = ['FailingAddress', 'RoutePlannerStatus']


class FailingAddress:
    """
    An address that has been marked as being ratelimited.
    """

    __slots__ = '_data', '_address', '_timestamp', '_time'

    def __init__(self, data: dict) -> None:
        self._data = data

        self._address = data.get('address')
        self._timestamp = data.get('timestamp')
        self._time = data.get('time')

    def __repr__(self) -> str:
        return f'<slate.FailingAddress address=\'{self.address}\' time=\'{self.time}\'>'

    @property
    def address(self) -> str:
        """
        :py:class:`str`:
            The address that was marked as failing.
        """
        return self._address

    @property
    def timestamp(self) -> int:
        """
        :py:class:`int`:
            The timestamp at which the address was marked as failing.
        """
        return self._timestamp

    @property
    def time(self) -> str:
        """
        :py:class:`str`:
            A formatted string detailing when this address was marked as failing.
        """
        return self._time


class RoutePlannerStatus:
    """
    Information about the status of the Route Planner.
    """

    __slots__ = '_data', '_rotator', '_ip_block_type', '_ip_block_size', '_failing_addresses'

    def __init__(self, data: dict) -> None:
        self._data = data

        self._rotator = data.get('class')

        details = data.get('details', {})

        ip_block = details.get('ipBlock', {})
        self._ip_block_type = ip_block.get('type')
        self._ip_block_size = ip_block.get('size')

        failing_addresses = details.get('failingAddresses', [])
        self._failing_addresses = [FailingAddress(dict(failing_address)) for failing_address in failing_addresses]

        # TODO blockIndex, currentAddressIndex, rotateIndex, ipIndex, currentAddress

    def __repr__(self) -> str:
        return f'<slate.RoutePlannerStatus rotator=\'{self.rotator}\' ip_block_size={self.ip_block_size} failing_addresses={len(self.failing_addresses)}>'

    @property
    def rotator(self) -> str:
        """
        :py:class:`str`:
            The type of rotator being used.
        """
        return self._rotator

    @property
    def ip_block_type(self) -> str:
        """
        :py:class:`str`:
            The type of IP block being used.
        """
        return self._ip_block_type

    @property
    def ip_block_size(self) -> str:
        """
        :py:class:`str`:
            The size of the IP block being used.
        """
        return self.ip_block_size

    @property
    def failing_addresses(self) -> List[FailingAddress]:
        """
        :py:class:`List` [ :py:class:`FailingAddresses` ]:
            A list of FailingAddress objects.
        """
        return self.failing_addresses
