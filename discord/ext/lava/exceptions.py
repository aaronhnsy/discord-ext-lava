
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
