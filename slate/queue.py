# Future
from __future__ import annotations

# Standard Library
import asyncio
import contextlib
import random
from collections import deque
from collections.abc import Iterator
from typing import Generic, SupportsIndex, overload

# Local
from .objects.enums import QueueLoopMode
from .types import QueueItemT


__all__ = (
    "Queue",
)


class Queue(Generic[QueueItemT]):

    __slots__ = ("_items", "_history", "_loop_mode", "_waiters", "_finished",)

    def __init__(self) -> None:

        self._items: list[QueueItemT] = []
        self._history: list[QueueItemT] = []

        self._loop_mode: QueueLoopMode = QueueLoopMode.DISABLED

        self._waiters: deque[asyncio.Future[None]] = deque()

        self._finished: asyncio.Event = asyncio.Event()
        self._finished.set()

    def __repr__(self) -> str:
        return f"<slate.Queue item_count={len(self._items)}>"

    def __len__(self) -> int:
        return self._items.__len__()

    @overload
    def __getitem__(self, index: SupportsIndex) -> QueueItemT:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[QueueItemT]:
        ...

    def __getitem__(self, index: SupportsIndex | slice) -> QueueItemT | list[QueueItemT]:
        return self._items.__getitem__(index)

    def __setitem__(self, index: SupportsIndex, value: QueueItemT) -> None:
        self._items.__setitem__(index, value)

    def __delitem__(self, index: SupportsIndex) -> None:
        self._items.__delitem__(index)

    def __iter__(self) -> Iterator[QueueItemT]:
        return self._items.__iter__()

    def __reversed__(self) -> Iterator[QueueItemT]:
        return self._items.__reversed__()

    def __contains__(self, item: QueueItemT) -> bool:
        return self._items.__contains__(item)

    def __bool__(self) -> bool:
        return bool(self._items.__len__())

    # Private methods

    def _wakeup_next(self) -> None:

        while self._waiters:

            if not (waiter := self._waiters.popleft()).done():
                waiter.set_result(None)
                break

    def _get(
        self,
        *,
        position: int,
        put_into_history: bool
    ) -> QueueItemT:

        item = self._items.pop(position)

        if put_into_history:
            self.put_into_history(item=item)

        if self._loop_mode is not QueueLoopMode.DISABLED:
            self._put(
                target=self._items,
                item=item,
                position=0 if self._loop_mode is QueueLoopMode.CURRENT else None
            )

        return item

    def _put(
        self,
        *,
        target: list[QueueItemT],
        item: QueueItemT | None = None,
        items: list[QueueItemT] | None = None,
        position: int | None = None
    ) -> None:

        if item and items:
            raise ValueError("Only one of 'item' and 'items' can be specified.")

        if item:
            if position is None:
                target.append(item)
            else:
                target.insert(position, item)

        elif items:
            if position is None:
                target.extend(items)
            else:
                for _index, _item, in enumerate(items):
                    target.insert(position + _index, _item)

        else:
            raise ValueError("One of 'item' or 'items' must be specified.")

        self._wakeup_next()

    # Misc

    @property
    def loop_mode(self) -> QueueLoopMode:
        """
        Returns the current queue loop mode.
        """
        return self._loop_mode

    def set_loop_mode(
        self,
        mode: QueueLoopMode,
        /
    ) -> None:
        """
        Sets the queue loop mode.

        Parameters
        ----------
        mode
            The loop mode to set.
        """
        self._loop_mode = mode

    @property
    def length(self) -> int:
        """
        Returns the amount of items in the queue.
        """
        return self._items.__len__()

    def is_empty(self) -> bool:
        """
        Returns ``True`` if the queue is empty, ``False`` if not.
        """
        return self._items.__len__() == 0

    def clear(self) -> None:
        """
        Removes all items from the queue.
        """
        self._items.clear()

    def reverse(self) -> None:
        """
        Reverses the order of the items in the queue.
        """
        self._items.reverse()

    def shuffle(self) -> None:
        """
        Shuffles the items in the queue.
        """
        random.shuffle(self._items)

    def reset(self) -> None:
        """
        Clears the queue and resets it internal state.
        """

        self.clear()

        for waiter in self._waiters:
            waiter.cancel()

        self._waiters.clear()

    # GET methods

    def get_from_front(
        self,
        *,
        put_into_history: bool = True
    ) -> QueueItemT:
        """
        Removes and returns the first item in the queue.

        .. admonition:: This method also:
            :class: note

            - Adds the item to the queue history if ``put_into_history`` is ``True``.
            - Puts the item back into the queue at the front if :attr:`Queue.loop_mode` is :attr:`QueueLoopMode.CURRENT`.
            - Puts the item back into the queue at the end if :attr:`Queue.loop_mode` is :attr:`QueueLoopMode.ALL`.

        Parameters
        ----------
        put_into_history
            Whether the item should be added to the queue history. Optional, defaults to ``True``.

        Raises
        ------
        :exc:`IndexError`
            If the queue is empty.

        Returns
        -------
        :class:`~slate.Track`
        """

        try:
            item = self._get(position=0, put_into_history=put_into_history)
        except IndexError:
            raise IndexError("The queue is empty.")

        return item

    def get_from_position(
        self,
        position: int,
        /, *,
        put_into_history: bool = True
    ) -> QueueItemT:
        """
        Removes and returns an item at the given position from the queue.

        The note from :meth:`Queue.get_from_front` also applies here.

        Parameters
        ----------
        position
            The position of the item to remove and return.
        put_into_history
            Whether the item should be added to the queue history. Optional, defaults to ``True``.

        Raises
        ------
        :exc:`IndexError`
            If there is no item at the given position.

        Returns
        -------
        :class:`~slate.Track`
        """

        try:
            item = self._get(position=position, put_into_history=put_into_history)
        except IndexError:
            raise IndexError("There is no item at the given position.")

        return item

    async def wait_for_item(
        self,
        *,
        put_into_history: bool = True
    ) -> QueueItemT:
        """
        Waits until an item has been added to the queue and returns it.

        Parameters
        ----------
        put_into_history
            Whether the item should be added to the queue history. Optional, defaults to ``True``.
        """

        while self.is_empty():

            loop = asyncio.get_event_loop()
            waiter = loop.create_future()

            self._waiters.append(waiter)

            try:
                await waiter

            except Exception:

                waiter.cancel()

                with contextlib.suppress(ValueError):
                    self._waiters.remove(waiter)

                if not self.is_empty() and not waiter.cancelled():
                    self._wakeup_next()

                raise

        return self.get_from_front(put_into_history=put_into_history)

    # PUT methods

    def put_at_front(
        self,
        *,
        item: QueueItemT | None = None,
        items: list[QueueItemT] | None = None
    ) -> None:
        """
        Puts an item, or items, into the front of the queue.

        Parameters
        ----------
        item
            The item to put into the queue.
        items
            The items to put into the queue.


        .. warning::

            Only one of ``item`` and ``items`` can be specified.

        Raises
        ------
        :exc:`ValueError`
            If both or none of ``item`` and ``items`` are specified.
        """
        self._put(target=self._items, item=item, items=items, position=0)

    def put_at_position(
        self,
        position: int,
        /, *,
        item: QueueItemT | None = None,
        items: list[QueueItemT] | None = None
    ) -> None:
        """
        Puts an item, or items, into the queue at the given position.

        Parameters
        ----------
        position
            The position to insert the item or items at.
        item
            The item to put into the queue.
        items
            The items to put into the queue.


        .. warning::

            Only one of ``item`` and ``items`` can be specified.

        Raises
        ------
        :exc:`ValueError`
            If both or none of ``item`` and ``items`` are specified.
        """
        self._put(target=self._items, item=item, items=items, position=position)

    def put_at_end(
        self,
        *,
        item: QueueItemT | None = None,
        items: list[QueueItemT] | None = None
    ) -> None:
        """
        Puts an item (or items) at the end of the queue.

        Parameters
        ----------
        item
            The item to put into the queue.
        items
            The items to put into the queue.


        .. warning::

            Only one of ``item`` and ``items`` can be specified.

        Raises
        ------
        :exc:`ValueError`
            If both or none of ``item`` and ``items`` are specified.
        """
        self._put(target=self._items, item=item, items=items, position=None)

    # History methods

    def get_from_history(
        self,
        *,
        position: int
    ) -> QueueItemT:
        """
        Get the item at the given position from the queue history.

        Parameters
        ----------
        position
            The position of the item to get from the queue history.

        Raises
        ------
        :exc:`IndexError`
            If there is no item at the given position.

        Returns
        -------
        :class:`~slate.Track`
        """

        try:
            item = self._history[-position]
        except IndexError:
            raise IndexError("There is no history item at the given position.")

        return item

    def pop_from_history(
        self,
        *,
        position: int
    ) -> QueueItemT:
        """
        Removes and returns the item at the given position from the queue history.

        Parameters
        ----------
        position
            The position of the item to remove and return from the queue history.

        Raises
        ------
        :exc:`IndexError`
            If there is no item at the given position.

        Returns
        -------
        :class:`~slate.Track`
        """

        try:
            item = self._history.pop(-position)
        except IndexError:
            raise IndexError("There is no history item at the given position.")

        return item

    def put_into_history(
        self,
        *,
        position: int | None = None,
        item: QueueItemT | None = None,
        items: list[QueueItemT] | None = None
    ) -> None:
        """
        Puts an item, or items, into the queue history at the given position.

        Parameters
        ----------
        position
            The position to insert the item or items at. Optional, defaults to ``None`` which adds the item(s) to
            the end of the history. (which means they will be fetched first by :meth:`Queue.get_from_history`)
        item
            The item to put into the queue history.
        items
            The items to put into the queue history.


        .. warning::

            Only one of ``item`` and ``items`` can be specified.

        Raises
        ------
        :exc:`ValueError`
            If both or none of ``item`` and ``items`` are specified.
        """
        self._put(target=self._history, item=item, items=items, position=position)
