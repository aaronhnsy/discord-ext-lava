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


JSONDumps = Callable[..., str]
JSONLoads = Callable[..., dict[str, Any]]

VoiceChannel = discord.VoiceChannel | discord.StageChannel

BotT = TypeVar("BotT", bound=discord.Client | discord.AutoShardedClient | commands.Bot | commands.AutoShardedBot)
ContextT = TypeVar("ContextT", bound=commands.Context[Any])
PlayerT = TypeVar("PlayerT", bound="Player[Any, Any, Any]")
