from __future__ import annotations

import logging
import random
from typing import Dict, Optional, Protocol, Type

import aiohttp
import discord

from slate.bases.node import BaseNode
from slate.bases.player import Player
from slate.exceptions import NoNodesAvailable, NodeCreationError, NodeNotFound, PlayerAlreadyExists

__log__ = logging.getLogger(__name__)
__all__ = ['Client']


class Client:
    """
    The client used to manage nodes and players.

    Parameters
    ----------
    bot: :py:class:`typing.Protocol` [ :py:class:`discord.Client` ]
        The bot instance that this client should be associated with.
    session: Optional [ :py:class:`aiohttp.ClientSession` ]
        The aiohttp client session used to make requests and connect to websockets with. If not passed, a new client session will be made.
    """

    def __init__(self, *, bot: Protocol[discord.Client], session: Optional[aiohttp.ClientSession] = None) -> None:

        self._bot: Protocol[discord.Client] = bot
        self._session: aiohttp.ClientSession = session or aiohttp.ClientSession()

        self._nodes: Dict[str, Protocol[BaseNode]] = {}

    def __repr__(self) -> str:
        return f'<slate.Client node_count={len(self.nodes)}>'

    #

    @property
    def bot(self) -> Protocol[discord.Client]:
        """
        :py:class:`Protocol` [ :py:class:`discord.Client` ]:
            The bot instance that this client is connected to.
        """
        return self._bot

    @property
    def session(self) -> aiohttp.ClientSession:
        """
        :py:class:`aiohttp.ClientSession`:
            The aiohttp session used to make requests and connect to node websockets with.
        """
        return self._session

    #

    @property
    def nodes(self) -> Dict[str, Protocol[BaseNode]]:
        """
        :py:class:`Dict` [ :py:class:`str` , :py:class:`typing.Protocol` [ :py:class:`BaseNode` ] ]:
            A mapping of node identifier's to nodes that this client is managing.
        """

        return self._nodes

    #

    async def create_node(self, *, host: str, port: str, password: str, identifier: str, cls: Type[Protocol[BaseNode]], **kwargs) -> Protocol[BaseNode]:
        """
        Creates a node and attempts to connect it to it's external websocket.

        Parameters
        ----------
        host: :py:class:`str`
            The host address to attempt connection with.
        port: :py:class:`int`
            The port to attempt connection with.
        password: :py:class:`str`
            The password used for authentification.
        identifier: :py:class:`str`
            A unique identifier used to refer to the created node.
        cls: :py:class:`typing.Type` [ :py:class:`typing.Protocol` [ :py:class:`BaseNode` ] ]
            The class used to connect to the external node. Must be a subclass of :py:class:`BaseNode`.
        **kwargs:
            Optional keyword arguments to pass to the created node.

        Returns
        -------
        :py:class:`typing.Protocol` [ :py:class:`BaseNode` ]
            The node that was created.

        Raises
        ------
        :py:class:`NodeCreationError`
            Either a node with the given identifier already exists, or the given class was not a subclass of :py:class:`BaseNode`.
        :py:class:`NodeConnectionError`
            There was an error while connecting to the external node. Could mean there was invalid authorization or an incorrect host address/port, etc.
        """

        await self.bot.wait_until_ready()

        if identifier in self.nodes.keys():
            raise NodeCreationError(f'Node with identifier \'{identifier}\' already exists.')

        if not issubclass(cls, BaseNode):
            raise NodeCreationError(f'The \'node\' argument must be a subclass of \'{BaseNode.__name__}\'.')

        node = cls(client=self, host=host, port=port, password=password, identifier=identifier, **kwargs)
        __log__.debug(f'NODE | Attempting \'{node.__class__.__name__}\' connection with identifier \'{identifier}\'.')

        await node.connect()
        return node

    def get_node(self, *, identifier: Optional[str] = None) -> Optional[Protocol[BaseNode]]:
        """
        Returns the node with the given identifier.

        Parameters
        ----------
        identifier: Optional [ :py:class:`str` ]
            The identifier of the node to return. If not passed a random node will be returned.

        Returns
        -------
        Optional [ :py:class:`typing.Protocol` [ :py:class:`BaseNode` ] ]
            The node that was found. Could return :py:class:`None` if no nodes with the given identifier were found.

        Raises
        ------
        :py:class:`NoNodesAvailable`
            Raised if there are no nodes available.
        """

        available_nodes = {identifier: node for identifier, node in self._nodes.items() if node.is_available}
        if not available_nodes:
            raise NoNodesAvailable('There are no Nodes available.')

        if identifier is None:
            return random.choice(list(available_nodes.values()))

        return available_nodes.get(identifier, None)

    async def create_player(self, *, channel: discord.VoiceChannel, node_identifier: Optional[str] = None, cls: Optional[Type[Protocol[Player]]] = Player) -> Protocol[Player]:
        """
        Creates a player for the given :py:class:`discord.VoiceChannel`.

        Parameters
        ----------
        channel: :py:class:`discord.VoiceChannel`
            The discord voice channel to connect the player too.
        node_identifier: Optional [ :py:class:`str` ]
            A node identifier to create the player on. If not passed a random node will be chosen.
        cls: :py:class:`typing.Type` [ :py:class:`typing.Protocol` [ :py:class:`Player` ] ]
            The class used to implement the base player features. Must be a subclass of :py:class:`Player`. Defaults to the player supplied with Slate.

        Returns
        -------
        :py:class:`typing.Protocol` [ :py:class:`Player` ]
            The player that was created.

        Raises
        ------
        :py:class:`NodeNotFound`
            Raised if a node with the given identifier was not found.
        :py:class:`NoNodesAvailable`
            Raised if there are no nodes available.
        :py:class:`PlayerAlreadyExists`
            Raised if a player for the voice channel already exists.
        """

        node = self.get_node(identifier=node_identifier)
        if not node and node_identifier:
            raise NodeNotFound(f'Node with identifier \'{node_identifier}\' was not found.')

        if channel.guild.voice_client:
            raise PlayerAlreadyExists(f'Player for guild \'{channel.guild.id}\' already exists.')

        __log__.debug(f'PLAYER | Creating player for channel \'{channel.id}\' in guild \'{channel.guild.id}\'.')

        player = await channel.connect(cls=cls)
        player._node = node

        node._players[channel.guild.id] = player
        return player
