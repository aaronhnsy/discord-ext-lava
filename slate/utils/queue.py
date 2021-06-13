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

import random
from collections import Iterator
from typing import Any, Generic, Optional, Union, TypeVar


__all__ = (
    'Queue',
)


Item = TypeVar('Item')


class Queue(Generic[Item]):

    def __init__(self) -> None:

        self._queue: list[Item] = []
        self._queue_history: list[Item] = []

        self._looping: bool = False
        self._looping_current: bool = False

    def __repr__(self) -> str:
        return f'<slate.Queue length={len(list(self.queue))} history_length={len(list(self.history))}>'

    def __len__(self) -> int:
        return len(self._queue)

    def __getitem__(self, key: int) -> Item:
        return self._queue[key]

    def __setitem__(self, key: int, value: Item) -> None:
        self._queue[key] = value

    def __delitem__(self, key: int) -> None:
        del self._queue[key]

    def __iter__(self) -> Iterator[Item]:
        return self._queue.__iter__()

    def __reversed__(self) -> Iterator[Item]:
        return self._queue.__reversed__()

    def __contains__(self, item: Item) -> bool:
        return item in self._queue

    def __add__(self, other: list[Item]) -> None:

        if not isinstance(other, list):
            raise TypeError(f'unsupported operand type(s) for +: \'list\' and \'{type(other)}\'')

        self._queue.extend(other)

    def __sub__(self, other: list[Item]) -> None:

        if not isinstance(other, list):
            raise TypeError(f'unsupported operand type(s) for -: \'list\' and \'{type(other)}\'')

        self._queue = [item for item in self._queue if item not in other]

    #

    @property
    def is_looping(self) -> bool:
        return self._looping

    @property
    def is_looping_current(self) -> bool:
        return self.is_looping and self._looping_current

    @property
    def is_empty(self) -> bool:
        return not self._queue

    #

    @property
    def queue(self) -> Iterator[Item]:
        yield from self._queue

    @property
    def history(self) -> Iterator[Item]:
        yield from self._queue_history[1:]

    #

    @staticmethod
    def _put(iterable: list[Any], items: Union[list[Item], Item], position: Optional[int] = None) -> None:

        if position is None:
            if isinstance(items, list):
                iterable.extend(items)
            else:
                iterable.append(items)

        else:
            if isinstance(items, list):
                for index, track, in enumerate(items):
                    iterable.insert(position + index, track)
            else:
                iterable.insert(position, items)

    #

    def get(self, position: int = 0, *, put_history: bool = True) -> Optional[Item]:

        try:

            item = self._queue.pop(position)

            if put_history:
                self.put_history(items=item, position=position)

            return item

        except IndexError:
            return None

    def put(self, items: Union[list[Item], Item], *, position: Optional[int] = None) -> None:
        self._put(iterable=self._queue, items=items, position=position)

    def shuffle(self) -> None:
        random.shuffle(self._queue)

    def reverse(self) -> None:
        self._queue.reverse()

    def clear(self) -> None:
        self._queue.clear()

    #

    def get_history(self, position: int = 0) -> Optional[Item]:

        try:
            return list(reversed(self._queue_history))[position]
        except IndexError:
            return None

    def put_history(self, items: Union[list[Item], Item], *, position: Optional[int] = None) -> None:
        self._put(iterable=self._queue_history, items=items, position=position)

    def shuffle_history(self) -> None:
        random.shuffle(self._queue_history)

    def reverse_history(self) -> None:
        self._queue_history.reverse()

    def clear_history(self) -> None:
        self._queue_history.clear()

    #

    def set_looping(self, *, looping: bool, current: bool = False):

        if looping:
            self._looping = True
            if current:
                self._looping_current = True
        else:
            self._looping = False
            if current:
                self._looping = True
                self._looping_current = True
