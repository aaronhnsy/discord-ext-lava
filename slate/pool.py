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
    """
    A mapping of node identifiers to nodes that are attached to this pool.
    """

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
        """
        Creates a new node, connects it to its provider server, and adds it to the pool.

        Parameters
        ----------
        bot
            The bot that this node should be attached to.
        session
            The session that this node will use for HTTP requests and WebSocket connections. Optional, if ``None``,
            a new session will be created and used.
        provider
            An enum value indicating which external application this node is connecting to.
        identifier
            A unique identifier for this node.
        host
            The host (ip address, in most cases) that this node will connect to.
        port
            The port that this node will connect with.
        password
            The password to use for HTTP requests and WebSocket connections with the provider server.
        secure
            Whether to use secure HTTP requests and WebSocket connections. Optional, defaults to ``False``.
        resume_key
            The resuming key to use when connecting to the provider server. Optional, defaults to ``None``.
        rest_url
            The url used to make HTTP requests to the provider server. Optional, if ``None``, the url will be
            constructed from the host and port.
        ws_url
            The url used for WebSocket connections with the provider server. Optional, if ``None``, the url will be
            constructed from the host and port.
        json_dumps
            The callable used to serialize JSON data. Optional, if ``None``, the built-in ``json.dumps`` will be used.
        json_loads
            The callable used to deserialize JSON data. Optional, if ``None``, the built-in ``json.loads`` will be used.
        spotify_client_id
            The spotify client ID to use for the builtin spotify integration. Optional, if ``None``, spotify
            support will be disabled.
        spotify_client_secret
            The spotify client secret to use for the builtin spotify integration. Optional, if ``None``, spotify
            support will be disabled.

        Raises
        ------
        :exc:`~slate.NodeAlreadyExists`
            If a node with the given identifier already exists.
        :exc:`~slate.InvalidNodePassword`
            If the password provided did not match the password required by the provider server.
        :exc:`~slate.NodeConnectionError`
            If the node could not connect to the provider server.

        Returns
        -------
        :class:`~slate.Node`
        """

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
        """
        Retrieves the node with the given identifier from the pool, or a random one if an identifier is not provided.

        Parameters
        ----------
        identifier
            The identifier of the node to return. Optional, if ``None``, a random node will be returned.

        Raises
        ------
        :exc:`~slate.NoNodesConnected`
            If there are no nodes attached to the pool.
        :exc:`~slate.NodeNotFound`
            If there are no nodes with the given identifier in the pool.

        Returns
        -------
        :class:`~slate.Node`
        """

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
        """
        Removes the node with the given identifier from the pool. This also calls the nodes :meth:`Node.disconnect`
        method which in turn calls each player's :meth:`Player.disconnect` method.

        Parameters
        ----------
        identifier
            The identifier of the node to remove.
        force
            See :meth:`Node.disconnect` and :meth:`Player.disconnect` for more information. Optional, defaults to
            ``False``.

        Returns
        -------
        ``None``
        """

        node: Node[BotT, PlayerT] = cls.get_node(identifier)
        await node.disconnect(force=force)

        del cls.nodes[node.identifier]
        __log__.info(f"Removed node '{identifier}' from the pool.")
