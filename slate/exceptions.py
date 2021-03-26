
__all__ = [
    'SlateException', 'NodeException', 'NodeCreationError', 'NodeConnectionError', 'NodeConnectionClosed', 'NodeNotFound', 'NoNodesAvailable', 'PlayerAlreadyExists',
    'TrackLoadFailed', 'TrackLoadError', 'TrackDecodeError'
]


class SlateException(Exception):
    """
    The base exception from which all Slate exceptions derive from.
    """
    pass


class NodeException(SlateException):
    """
    Base for exceptions raised for Node related errors.
    """
    pass


class NodeCreationError(NodeException):
    """
    Raised when there was an error creating a Node such as a duplicate identifier or the Node class being passed to :py:meth:`Client.create_node` not being a subclass of
    :py:class:`BaseNode`.
    """
    pass


class NodeConnectionError(NodeException):
    """
    Raised when there was an error while connecting to Nodes external websocket. Could be something like invalid passwords, host address's, ports, etc.
    """
    pass


class NodeConnectionClosed(NodeException):
    """
    Raised when a Nodes connection with its external websocket was closed.
    """
    pass


class NodeNotFound(NodeException):
    """
    Raised when a Node with the given identifier was not found.
    """
    pass


class NoNodesAvailable(NodeException):
    """
    Raised when there are no Nodes available. A Node is available when its websocket is connected and not closed.
    """
    pass


class PlayerAlreadyExists(SlateException):
    """
    Raised when a Player for the given channel's guild already exists.
    """
    pass


class TrackLoadFailed(SlateException):
    """
    Raised when an external node returns an error for searching for tracks or playlists.
    """

    def __init__(self, data: dict) -> None:

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
        """:py:class:`str`
            The error message returned from the external node. Should be safe to show to end users.
        """
        return self._message

    @property
    def severity(self) -> str:
        """:py:class:`str`:
            A string denoting the severity of the error. See this `file <https://github.com/sedmelluq/lavaplayer/blob/01dfac5fea1bf683d2a9bc8c8c28589099eb2540/main/src/main/java/com/sedmelluq/discord/lavaplayer/tools/FriendlyException.java#L26-L43>`_
            for more information.
        """
        return self._severity


class TrackLoadError(SlateException):
    """
    Raised when there was an error while using the external node to search for tracks or playlists.
    """

    def __init__(self, message: str, status_code: int) -> None:

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
            The HTTP status code returned for the search operation that failed.
        """
        return self._status_code


class TrackDecodeError(SlateException):

    def __init__(self, message: str, status_code: int) -> None:

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
            The HTTP status code returned for the search operation.
        """
        return self._status_code
