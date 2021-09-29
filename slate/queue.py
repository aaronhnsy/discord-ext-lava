# Future
from __future__ import annotations

# Standard Library
import random
from collections.abc import Iterator
from typing import Any, Generic, Literal, TypeVar, overload

# My stuff
from slate.objects.enums import QueueLoopMode


__all__ = (
    "Queue",
)

Item = TypeVar("Item")


class Queue(Generic[Item]):

    def __init__(self) -> None:

        self._queue: list[Item] = []
        self._queue_history: list[Item] = []

        self._loop_mode: QueueLoopMode = QueueLoopMode.OFF

    def __repr__(self) -> str:
        return f"<slate.Queue>"

    def __len__(self) -> int:
        return self._queue.__len__()

    def __getitem__(self, index: Any) -> Item:
        return self._queue.__getitem__(index)

    def __setitem__(self, index: Any, value: Item) -> None:
        self._queue.__setitem__(index, value)

    def __delitem__(self, index: int) -> None:
        self._queue.__delitem__(index)

    def __iter__(self) -> Iterator[Item]:
        return self._queue.__iter__()

    def __reversed__(self) -> Iterator[Item]:
        return self._queue.__reversed__()

    def __contains__(self, item: Item) -> bool:
        return self._queue.__contains__(item)

    #

    @property
    def loop_mode(self) -> QueueLoopMode:
        return self._loop_mode

    def set_loop_mode(
        self,
        mode: QueueLoopMode,
        /
    ) -> None:

        self._loop_mode = mode

    #

    @property
    def queue(self) -> Iterator[Item]:
        yield from self._queue

    @property
    def history(self) -> Iterator[Item]:
        yield from self._queue_history[1:]

    #

    @staticmethod
    def _put(
        iterable: list[Any],
        /,
        *,
        items: list[Item] | Item,
        position: int | None = None
    ) -> None:

        if position is None:
            if isinstance(items, list):
                iterable.extend(items)
            else:
                iterable.append(items)

        elif isinstance(items, list):
            for index, track, in enumerate(items):
                iterable.insert(position + index, track)
        else:
            iterable.insert(position, items)

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    #

    @overload
    def get(
        self,
        position: Literal[0] = 0,
        /,
        *,
        put_history: bool = True
    ) -> Item:
        ...

    @overload
    def get(
        self,
        position: int = 0,
        /,
        *,
        put_history: bool = True
    ) -> Item | None:
        ...

    def get(
        self,
        position: int = 0,
        /,
        *,
        put_history: bool = True
    ) -> Item | None:

        try:
            item = self._queue.pop(position)
        except IndexError:
            return None

        if put_history:
            self.put_history(item, position=position)

        if self._loop_mode is not QueueLoopMode.OFF:
            self.put(item, position=0 if self._loop_mode is QueueLoopMode.CURRENT else None)

        return item

    def put(
        self,
        items: list[Item] | Item,
        /,
        *,
        position: int | None = None
    ) -> None:

        self._put(self._queue, items=items, position=position)

    def shuffle(self) -> None:
        random.shuffle(self._queue)

    def reverse(self) -> None:
        self._queue.reverse()

    def clear(self) -> None:
        self._queue.clear()

    #

    def get_history(
        self,
        position: int = 0,
        /,
    ) -> Item | None:

        try:
            item = list(reversed(self._queue_history))[position]
        except IndexError:
            return None

        return item

    def put_history(
        self,
        items: list[Item] | Item,
        /,
        *,
        position: int | None = None
    ) -> None:

        self._put(self._queue_history, items=items, position=position)

    def shuffle_history(self) -> None:
        random.shuffle(self._queue_history)

    def reverse_history(self) -> None:
        self._queue_history.reverse()

    def clear_history(self) -> None:
        self._queue_history.clear()
