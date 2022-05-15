# Future
from __future__ import annotations

# Standard Library
import logging
from typing import Generic

# Packages
import aiohttp

# Local
from .exceptions import NodeAlreadyExists, NodeNotFound, NoNodesConnected
from .node import Node
from .objects.enums import Provider
from .types import BotT, JSONDumps, JSONLoads, PlayerT


__all__ = (
    "Pool",
)
__log__: logging.Logger = logging.getLogger("slate.pool")


class Pool(Generic[BotT, PlayerT]):

    def __repr__(self) -> str:
        return f"<slate.Pool node_count={len(self.nodes)}>"

    nodes: dict[str, Node[BotT, PlayerT]] = {}

    @classmethod
    async def create_node(
        cls,
        *,
        bot: BotT,
        session: aiohttp.ClientSession | None = None,
        # Connection information
        provider: Provider,
        identifier: str,
        host: str,
        port: str,
        password: str,
        secure: bool = False,
        resume_key: str | None = None,
        # URLs
        rest_url: str | None = None,
        ws_url: str | None = None,
        # JSON callables
        json_dumps: JSONDumps | None = None,
        json_loads: JSONLoads | None = None,
        # Spotify
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> Node[BotT, PlayerT]:

        if identifier in cls.nodes:
            raise NodeAlreadyExists(f"A node with the identifier '{identifier}' already exists.")

        node: Node[BotT, PlayerT] = Node(
            bot=bot,
            session=session,
            provider=provider,
            identifier=identifier,
            host=host,
            port=port,
            password=password,
            secure=secure,
            resume_key=resume_key,
            rest_url=rest_url,
            ws_url=ws_url,
            json_dumps=json_dumps,
            json_loads=json_loads,
            spotify_client_id=spotify_client_id,
            spotify_client_secret=spotify_client_secret,
        )
        await node.connect()

        cls.nodes[identifier] = node
        __log__.info(f"Added node '{node.identifier}' to the pool.")

        return node

    @classmethod
    def get_node(
        cls,
        identifier: str | None = None,
    ) -> Node[BotT, PlayerT]:

        if not cls.nodes:
            raise NoNodesConnected("There are no nodes connected.")

        if not identifier:
            return list(cls.nodes.values())[0]

        if node := cls.nodes.get(identifier):
            return node

        raise NodeNotFound(f"A node with the identifier '{identifier}' was not found.")

    @classmethod
    async def remove_node(
        cls,
        identifier: str,
        *,
        force: bool = False,
    ) -> None:

        node: Node[BotT, PlayerT] = cls.get_node(identifier)
        await node.disconnect(force=force)

        del cls.nodes[node.identifier]
        __log__.info(f"Removed node '{identifier}' from the pool.")
