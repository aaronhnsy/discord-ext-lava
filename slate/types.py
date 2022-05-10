# Future
from __future__ import annotations

# Standard Library
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

# Packages
import discord
from discord.ext import commands


if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    # Local
    from .player import Player


__all__ = (
    "JSONDumps",
    "JSONLoads",
    "VoiceChannel",
    "BotT",
    "PlayerT",
)


JSONDumps = Callable[..., str]
JSONLoads = Callable[..., dict[str, Any]]

VoiceChannel = discord.VoiceChannel | discord.StageChannel

BotT = TypeVar("BotT", bound=commands.Bot | commands.AutoShardedBot)
PlayerT = TypeVar("PlayerT", bound="Player[Any, Any]")
