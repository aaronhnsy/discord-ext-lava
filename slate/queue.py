# Future
from __future__ import annotations

# Standard Library
import asyncio
import random
from collections import deque
from collections.abc import Iterator
from typing import Any, Generic, TypeVar

# Local
from slate.objects.enums import QueueLoopMode


__all__ = (
    "Queue",
)

Item = TypeVar("Item")


class Queue(Generic[Item]):

    def __init__(self) -> None:

        self._queue: list[Item] = []
        self._history: list[Item] = []

        self._loop_mode: QueueLoopMode = QueueLoopMode.OFF

        self._waiters: deque[Any] = deque()

        self._finished: asyncio.Event = asyncio.Event()
        self._finished.set()

    def __repr__(self) -> str:
        return "<slate.Queue>"

    def __str__(self) -> str:
        return str([track.__str__() for track in self._queue])

    def __len__(self) -> int:
        return self._queue.__len__()

    def __getitem__(self, index: Any) -> Item:
        return self._queue.__getitem__(index)

    def __setitem__(self, index: Any, value: Item) -> None:
        self._queue.__setitem__(index, value)

    def __delitem__(self, index: Any) -> None:
        self._queue.__delitem__(index)

    def __iter__(self) -> Iterator[Item]:
        return self._queue.__iter__()

    def __reversed__(self) -> Iterator[Item]:
        return self._queue.__reversed__()

    def __contains__(self, item: Item) -> bool:
        return self._queue.__contains__(item)

    # Properties

    @property
    def length(self) -> int:
        return self._queue.__len__()

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    @property
    def loop_mode(self) -> QueueLoopMode:
        return self._loop_mode

    def set_loop_mode(self, mode: QueueLoopMode, /) -> None:
        self._loop_mode = mode

    # Normal methods

    def get(
        self,
        position: int = 0,
        /, *,
        put_history: bool = True
    ) -> Item | None:

        try:
            item = self._queue.pop(position)
        except IndexError:
            return None

        if put_history:
            self.put_history(item)

        if self._loop_mode is not QueueLoopMode.OFF:
            self.put(item, position=0 if self._loop_mode is QueueLoopMode.CURRENT else None)

        return item

    def put(
        self,
        item: Item,
        /, *,
        position: int | None = None
    ) -> None:

        if position is None:
            self._queue.append(item)
        else:
            self._queue.insert(position, item)

        self._wakeup_next()

    def extend(
        self,
        items: list[Item],
        /, *,
        position: int | None = None
    ) -> None:

        if position is None:
            self._queue.extend(items)
        else:
            for index, track, in enumerate(items):
                self._queue.insert(position + index, track)

        self._wakeup_next()

    # Wait methods

    def _wakeup_next(self) -> None:

        while self._waiters:

            if not (waiter := self._waiters.popleft()).done():
                waiter.set_result(None)
                break

    async def get_wait(self) -> Item:

        while self.is_empty():

            loop = asyncio.get_event_loop()
            waiter = loop.create_future()

            self._waiters.append(waiter)

            try:
                await waiter

            except Exception:

                waiter.cancel()

                try:
                    self._waiters.remove(waiter)
                except ValueError:
                    pass

                if not self.is_empty() and not waiter.cancelled():
                    self._wakeup_next()

                raise

        return self.get()  # type: ignore

    # History

    def get_history(
        self,
        position: int = 0,
        /,
    ) -> Item | None:

        try:
            item = list(reversed(self._history))[position]
        except IndexError:
            return None

        return item

    def put_history(
        self,
        item: Item,
        /, *,
        position: int | None = None
    ) -> None:

        if position is None:
            self._history.append(item)
        else:
            self._history.insert(position, item)

    def extend_history(
        self,
        items: list[Item],
        /, *,
        position: int | None = None
    ) -> None:

        if position is None:
            self._history.extend(items)
        else:
            for index, track, in enumerate(items):
                self._history.insert(position + index, track)

    # Misc

    def shuffle(self) -> None:
        random.shuffle(self._queue)

    def reverse(self) -> None:
        self._queue.reverse()

    def clear(self) -> None:
        self._queue.clear()
        self._history.clear()

    def reset(self) -> None:

        self.clear()

        for waiter in self._waiters:
            waiter.cancel()

        self._waiters.clear()
