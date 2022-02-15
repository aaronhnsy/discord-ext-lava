# Future
from __future__ import annotations

# Standard Library
import logging
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar, Union

# Packages
import aiohttp
import discord
from discord.ext import commands

# My stuff
from .exceptions import NodeCreationError, NodeNotFound, NoNodesConnected
from .node import Node
from .objects.enums import Provider


if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    # My stuff
    from .player import Player


__all__ = (
    "Pool",
)
__log__: logging.Logger = logging.getLogger("slate.pool")


BotT = TypeVar("BotT", bound=Union[discord.Client, discord.AutoShardedClient, commands.Bot, commands.AutoShardedBot])
ContextT = TypeVar("ContextT", bound=commands.Context)
PlayerT = TypeVar("PlayerT", bound="Player")  # type: ignore


class Pool(Generic[BotT, ContextT, PlayerT]):

    def __repr__(self) -> str:
        return "<slate.Pool>"

    nodes: dict[str, Node[BotT, ContextT, PlayerT]] = {}

    @classmethod
    async def create_node(
        cls,
        provider: Provider, /,
        *,
        bot: BotT,
        identifier: str,
        host: str,
        port: str,
        password: str,
        resume_key: str | None = None,
        rest_url: str | None = None,
        ws_url: str | None = None,
        json_dumps: Callable[..., str] | None = None,
        json_loads: Callable[..., dict[str, Any]] | None = None,
        session: aiohttp.ClientSession | None = None,
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> Node[BotT, ContextT, PlayerT]:

        if identifier in cls.nodes:
            raise NodeCreationError(f"A Node with the identifier '{identifier}' already exists.")

        node = Node(
            provider=provider,
            bot=bot,
            identifier=identifier,
            host=host,
            port=port,
            password=password,
            resume_key=resume_key,
            rest_url=rest_url,
            ws_url=ws_url,
            json_dumps=json_dumps,
            json_loads=json_loads,
            session=session,
            spotify_client_id=spotify_client_id,
            spotify_client_secret=spotify_client_secret,
        )

        await node.connect()
        cls.nodes[node._identifier] = node

        return node

    @classmethod
    def get_node(
        cls,
        *,
        identifier: str | None = None
    ) -> Node[BotT, ContextT, PlayerT]:

        if identifier:

            if not (node := cls.nodes.get(identifier)):
                raise NodeNotFound(f"There are no Nodes with the identifier '{identifier}'.")

            return node

        if not cls.nodes:
            raise NoNodesConnected("There are no Nodes connected.")

        return list(cls.nodes.values())[0]

    @classmethod
    async def remove_node(
        cls,
        identifier: str, /,
        *,
        force: bool = False
    ) -> None:

        node = cls.get_node(identifier=identifier)

        await node.disconnect(force=force)
        del cls.nodes[node._identifier]

        __log__.info(f"Node '{node._identifier}' removed.")
