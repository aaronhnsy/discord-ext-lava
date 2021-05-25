
__all__ = [
    'SlateException', 'NodeException', 'NodeConnectionError', 'NodeConnectionClosed', 'NodeNotFound', 'NoNodesAvailable', 'PlayerAlreadyExists', 'TrackLoadFailed', 'HTTPError'
]


class SlateException(Exception):
    """
    The base exception from which all Slate exceptions derive from.
    """


class NodeException(SlateException):
    """
    Base for exceptions raised for node related errors.
    """


class NodeConnectionError(NodeException):
    """
    Raised when there was an error while connecting to a nodes external websocket. Could be something like invalid passwords, host address's, ports, etc.
    """


class NodeConnectionClosed(NodeException):
    """
    Raised when a nodes connection with it's external websocket was closed.
    """


class NodeNotFound(NodeException):
    """
    Raised when a node with the given identifier was not found.
    """


class NoNodesAvailable(NodeException):
    """
    Raised when there are no nodes available. A node is available when it's websocket is connected and not closed.
    """


class PlayerAlreadyExists(SlateException):
    """
    Raised when a player for the given channel's guild already exists.
    """


class TrackLoadFailed(SlateException):
    """
    Raised when there is an error while loading tracks or playlists.

    Parameters
    ----------
    data: dict
        Information about the error.
    """

    def __init__(self, data: dict):
        super().__init__()

        self._data = data

        exception = data.get('exception')
        if exception:
            self._message = exception.get('message')
            self._severity = exception.get('severity')
        else:
            cause = data.get('cause')
            self._message = cause.get('message')
            self._severity = data.get('severity')

            self._class = cause.get('class')
            self._stack = cause.get('stack')
            self._cause = cause.get('cause')
            self._suppressed = cause.get('suppressed')

    @property
    def message(self) -> str:
        """
        :py:class:`str`
            An error message. Should be safe to show to end users.
        """
        return self._message

    @property
    def severity(self) -> str:
        """
        :py:class:`str`:
            The severity of the error. See this `file <https://github.com/sedmelluq/lavaplayer/blob/01dfac5fea1bf683d2a9bc8c8c28589099eb2540/main/src/main/java/com/sedmelluq
            /discord/lavaplayer/tools/FriendlyException.java#L26-L43>`_ for more information.
        """
        return self._severity


class HTTPError(SlateException):
    """
    Raised when there is an error during a HTTP operation.

    Parameters
    ----------
    message: str
        A message for what happened to cause this error.
    status_code: int
        The status code returned by the HTTP operation.
    """

    def __init__(self, message: str, status_code: int):
        super().__init__()

        self._message = message
        self._status_code = status_code

    @property
    def message(self) -> str:
        """
        :py:class:`str`:
            A message for what happened to cause this error.
        """
        return self._message

    @property
    def status_code(self) -> int:
        """
        :py:class:`int`:
            The status code returned by the HTTP operation.
        """
        return self._status_code
