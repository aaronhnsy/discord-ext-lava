from __future__ import annotations

from typing import TypedDict


__all__ = (
    "ChannelMixData",
    "ChannelMix",
)


class ChannelMixData(TypedDict):
    leftToLeft: float
    leftToRight: float
    rightToLeft: float
    rightToRight: float


class ChannelMix:

    __slots__ = ("left_to_left", "left_to_right", "right_to_left", "right_to_right",)

    def __init__(
        self,
        *,
        left_to_left: float = 1.0,
        left_to_right: float = 0.0,
        right_to_left: float = 0.0,
        right_to_right: float = 1.0,
    ) -> None:

        if any(
            value for value in (left_to_left, left_to_right, right_to_left, right_to_right) if
            value < 0.0 or value > 1.0
        ):
            raise ValueError(
                "'left_to_left', 'left_to_right', 'right_to_left', and 'right_to_right' must all be between "
                "(or equal to) 0.0 and 1.0."
            )

        self.left_to_left: float = left_to_left
        self.left_to_right: float = left_to_right
        self.right_to_left: float = right_to_left
        self.right_to_right: float = right_to_right

    def __repr__(self) -> str:
        return f"<discord.ext.lava.ChannelMix " \
               f"left_to_left={self.left_to_left}, " \
               f"left_to_right={self.left_to_right}, " \
               f"right_to_left={self.right_to_left}, " \
               f"right_to_right{self.right_to_right}>"

    def construct_payload(self) -> ChannelMixData:
        return {
            "leftToLeft":   self.left_to_left,
            "leftToRight":  self.left_to_right,
            "rightToLeft":  self.right_to_left,
            "rightToRight": self.right_to_right,
        }

    @classmethod
    def mono(cls) -> ChannelMix:
        return cls(left_to_left=0.5, left_to_right=0.5, right_to_left=0.5, right_to_right=0.5)

    @classmethod
    def only_left(cls) -> ChannelMix:
        return cls(left_to_left=1.0, left_to_right=0.0, right_to_left=0.0, right_to_right=0.0)

    @classmethod
    def full_left(cls) -> ChannelMix:
        return cls(left_to_left=0.5, left_to_right=0.0, right_to_left=0.5, right_to_right=0.0)

    @classmethod
    def only_right(cls) -> ChannelMix:
        return cls(left_to_left=0.0, left_to_right=0.0, right_to_left=0.0, right_to_right=1.0)

    @classmethod
    def full_right(cls) -> ChannelMix:
        return cls(left_to_left=0.0, left_to_right=0.5, right_to_left=0.0, right_to_right=0.5)

    @classmethod
    def switch(cls) -> ChannelMix:
        return cls(left_to_left=0.0, left_to_right=1.0, right_to_left=1.0, right_to_right=0.0)
