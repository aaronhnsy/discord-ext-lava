# Future
from __future__ import annotations

# Standard Library
import logging
from typing import Generic

# Local
from .exceptions import NodeAlreadyExists, NodeNotFound, NoNodesConnected
from .node import Node
from .objects.enums import Provider
from .types import BotT, JSONDumps, JSONLoads, PlayerT


__all__ = (
    "Pool",
)


LOGGER: logging.Logger = logging.getLogger("slate.pool")


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
        provider: Provider,
        identifier: str,
        host: str | None = None,
        port: str | None = None,
        ws_url: str | None = None,
        rest_url: str | None = None,
        password: str | None = None,
        # JSON Callables
        json_dumps: JSONDumps | None = None,
        json_loads: JSONLoads | None = None,
        # Spotify
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
    ) -> Node[BotT, PlayerT]:
        """
        Creates a new node, connects it to its provider server, and adds it to the pool.

        .. note::

            You must set either the host and port or ws_url and rest_url parameters.


        Parameters
        ----------
        bot
            The bot instance that this node should be attached to.
        provider
            An enum value representing which provider server this node is connecting to.
        identifier
            A unique identifier for this node.
        host
            The host that this node will use for WebSocket connections and HTTP requests. If you want to construct a
            ``ws_url`` and ``rest_url`` yourself, you can pass ``None`` for this parameter.
        port
            The port that this node will use for WebSocket connections and HTTP requests. If you want to construct a
            ``ws_url`` and ``rest_url`` yourself, you can pass ``None`` for this parameter.
        ws_url
            The url that will be used to connect to the websocket. Constructing this url manually is optional and will
            override the ``host`` and ``port`` parameters.
        rest_url
            The url that will be used to make HTTP requests. Constructing this url manually is optional and will
            override the ``host`` and ``port`` parameters.
        password
            The password to use for connections with the provider server. If the provider server does not require a
            password you can omit this parameter by passing ``None``.
        json_dumps
            The callable that will be used to serialize JSON data. Optional, if ``None``, the built-in ``json.dumps``
            will be used.
        json_loads
            The callable that will be used to deserialize JSON data. Optional, if ``None``, the built-in ``json.loads``
            will be used.
        spotify_client_id
            The spotify client ID to use for the builtin spotify integration. Optional, if ``None``, spotify
            support will be disabled.
        spotify_client_secret
            The spotify client secret to use for the builtin spotify integration. Optional, if ``None``, spotify
            support will be disabled.

        Raises
        ------
        :exc:`ValueError`
            If you don't provide either ``host`` and ``port`` or ``ws_url`` and ``rest_url``.
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
            provider=provider,
            identifier=identifier,
            host=host,
            port=port,
            password=password,
            rest_url=rest_url,
            ws_url=ws_url,
            json_dumps=json_dumps,
            json_loads=json_loads,
            spotify_client_id=spotify_client_id,
            spotify_client_secret=spotify_client_secret,
        )
        await node.connect()

        cls.nodes[identifier] = node
        LOGGER.info(f"Node '{node.identifier}' has been added to the pool.")

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
    ) -> None:
        """
        Removes the node with the given identifier from the pool. This also calls the nodes :meth:`Node.disconnect`
        method which in turn calls each player's :meth:`Player.disconnect` method.

        Parameters
        ----------
        identifier
            The identifier of the node to remove.
        """

        node: Node[BotT, PlayerT] = cls.get_node(identifier)
        await node.disconnect()

        del cls.nodes[node.identifier]
        LOGGER.info(f"Node '{identifier}' has been removed from the pool.")
