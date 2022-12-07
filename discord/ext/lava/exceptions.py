from __future__ import annotations


__all__: list[str] = [
    "LavaError",
    "NodeAlreadyConnected",
    "NodeConnectionError",
]


class LavaError(Exception):
    pass


class NodeAlreadyConnected(LavaError):
    pass


class NodeConnectionError(LavaError):
    pass
