# Future
from __future__ import annotations

# Standard Library
import logging
from typing import Generic

# Packages
import aiohttp

# Local
from .exceptions import NodeCreationError, NodeNotFound, NoNodesConnected
from .node import Node
from .objects.enums import Provider
from .types import BotT, ContextT, JSONDumps, JSONLoads, PlayerT


__all__ = (
    "Pool",
)
__log__: logging.Logger = logging.getLogger("slate.pool")


class Pool(Generic[BotT, ContextT, PlayerT]):

    nodes: dict[str, Node[BotT, ContextT, PlayerT]] = {}

    def __repr__(self) -> str:
        return "<slate.Pool>"

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
        json_dumps: JSONDumps | None = None,
        json_loads: JSONLoads | None = None,
        session: aiohttp.ClientSession | None = None,
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> Node[BotT, ContextT, PlayerT]:

        if identifier in cls.nodes:
            raise NodeCreationError(f"A Node with the identifier '{identifier}' already exists.")

        node: Node[BotT, ContextT, PlayerT] = Node(
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

        cls.nodes[identifier] = node
        __log__.info(f"Node '{node.identifier}' added to Pool.")

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

        node = cls.get_node(
            identifier=identifier
        )
        await node.disconnect(force=force)

        del cls.nodes[node.identifier]
        __log__.info(f"Node '{node.identifier}' removed from Pool.")
