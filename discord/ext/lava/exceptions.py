from __future__ import annotations


__all__: list[str] = [
    "LavaError",
    "NodeAlreadyConnected",
    "NodeConnectionError",
    "NodeNotReady",
]


class LavaError(Exception):
    pass


class NodeAlreadyConnected(LavaError):
    pass


class NodeConnectionError(LavaError):
    pass


class NodeNotReady(LavaError):
    pass
