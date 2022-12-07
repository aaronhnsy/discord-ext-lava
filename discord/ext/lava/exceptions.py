from __future__ import annotations


__all__ = (
    "LavaError",
    "NodeAlreadyConnected",
    "NodeConnectionError",
)


class LavaError(Exception):
    pass


class NodeAlreadyConnected(LavaError):
    pass


class NodeConnectionError(LavaError):
    pass
