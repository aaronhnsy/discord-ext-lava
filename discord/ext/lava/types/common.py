from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias

import discord


JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

JSONDumps: TypeAlias = Callable[[JSON], str]
JSONLoads: TypeAlias = Callable[..., JSON]

VoiceChannel: TypeAlias = discord.VoiceChannel | discord.StageChannel
