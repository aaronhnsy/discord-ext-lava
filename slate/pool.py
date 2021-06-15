"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import logging
import uuid
from typing import Generic, Optional, TYPE_CHECKING, Type, TypeVar, Union

import discord
from discord.ext import commands

from .exceptions import NodeAlreadyExists, NodeNotFound, NodesNotFound


if TYPE_CHECKING:

    from typing import Any

    from .obsidian.node import ObsidianNode
    from .lavalink.node import LavalinkNode
    from .andesite.node import AndesiteNode


__all__ = ['NodePool']
__log__: logging.Logger = logging.getLogger('slate.pool')


BotT = TypeVar('BotT', bound=Union[discord.Client, commands.Bot, commands.AutoShardedBot])
NodeT = TypeVar('NodeT', bound=Union['ObsidianNode[Any, Any]', 'LavalinkNode[Any]', 'AndesiteNode[Any]'])


class NodePool(Generic[BotT, NodeT]):

    def __repr__(self) -> str:
        return '<slate.NodePool>'

    #

    _nodes: dict[str, NodeT] = {}

    @property
    def nodes(self) -> dict[str, NodeT]:
        return self._nodes

    #

    @classmethod
    async def create_node(
            cls, *, type: Type[NodeT], bot: BotT, host: str, port: str, password: str, identifier: Optional[str] = None, region: Optional[discord.VoiceRegion] = None, **kwargs
    ) -> NodeT:

        identifier = identifier or str(uuid.uuid4())
        if identifier in cls._nodes:
            raise NodeAlreadyExists(f'Node with identifier \'{identifier}\' already exists.')

        node = type(bot, host, port, password, identifier, region, **kwargs)
        await node.connect()

        cls._nodes[node.identifier] = node
        return node

    @classmethod
    def get_node(cls, node_cls: Type[NodeT], identifier: Optional[str] = None) -> NodeT:

        nodes = {identifier: node for identifier, node in cls._nodes.items() if type(node) is node_cls}

        if not nodes:
            raise NodesNotFound('There are no nodes connected.')

        if identifier:

            if not (node := nodes.get(identifier)):
                raise NodeNotFound(f'A node with identifier \'{identifier}\' was not found.')

            return node

        return list(nodes.values())[0]
