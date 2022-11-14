
__all__ = (
    "LavaError",
    "NodeConnectionError",
    "AlreadyConnected",
    "IncorrectPassword",
)


class LavaError(Exception):
    pass


class NodeConnectionError(LavaError):
    pass


class AlreadyConnected(NodeConnectionError):
    pass


class IncorrectPassword(NodeConnectionError):
    pass

