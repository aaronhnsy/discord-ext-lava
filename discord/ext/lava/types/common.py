from collections.abc import Callable
from typing import Any

import discord
from typing_extensions import TypeVar

from ..player import Player


__all__ = (
    "JSONDumps",
    "JSONLoads",
    "ClientT",
    "PlayerT"
)

ClientT = TypeVar("ClientT", bound=discord.Client | discord.AutoShardedClient, default=discord.Client)
PlayerT = TypeVar("PlayerT", bound=Player, default=Player)

JSONDumps = Callable[..., str]
JSONLoads = Callable[..., dict[str, Any]]
