
__all__ = [
    "LavaError",
    "LinkAlreadyConnected",
    "LinkConnectionError",
    "LinkNotReady",
]


class LavaError(Exception):
    pass


class LinkAlreadyConnected(LavaError):
    pass


class LinkConnectionError(LavaError):
    pass


class LinkNotReady(LavaError):
    pass
