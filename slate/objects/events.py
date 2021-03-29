from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from slate.bases.player import Player


__all__ = ['TrackStartEvent', 'TrackEndEvent', 'TrackExceptionEvent', 'TrackStuckEvent', 'WebSocketClosedEvent']


class TrackStartEvent:

    __slots__ = 'data', 'player', 'track'

    def __init__(self, data: dict) -> None:

        self.data: dict = data

        self.player: Protocol[Player] = data.get('player')
        self.track: str = data.get('track')

    def __repr__(self) -> str:
        return f'<slate.TrackStartEvent player={self.player!r} track=\'{self.track}\''

    def __str__(self) -> str:
        return 'track_start'


class TrackEndEvent:

    __slots__ = 'data', 'player', 'track', 'reason', 'may_start_next'

    def __init__(self, data: dict) -> None:

        self.data: dict = data

        self.player: Protocol[Player] = data.get('player')
        self.track: str = data.get('track')

        self.reason: str = data.get('reason')
        self.may_start_next: bool = data.get('mayStartNext', False)

    def __repr__(self) -> str:
        return f'<slate.TrackEndEvent player={self.player!r} track=\'{self.track}\' reason=\'{self.reason}\''

    def __str__(self) -> str:
        return 'track_end'


class TrackExceptionEvent:

    __slots__ = 'data', 'player', 'track', 'message', 'cause', 'stack', 'suppressed', 'severity'

    def __init__(self, data: dict) -> None:

        self.data: dict = data

        self.player: Protocol[Player] = data.get('player')
        self.track: str = data.get('track')

        exception = data.get('exception')
        self.message: str = exception.get('message')
        self.cause: str = exception.get('cause', None)
        self.stack: str = exception.get('stack', [])
        self.suppressed: str = exception.get('suppressed', [])
        self.severity: str = exception.get('severity', 'UNKNOWN')

    def __repr__(self) -> str:
        return f'<slate.TrackExceptionEvent player={self.player} track=\'{self.track}\' message=\'{self.message}\' severity=\'{self.severity}\' cause=\'{self.cause}\''

    def __str__(self) -> str:
        return 'track_exception'


class TrackStuckEvent:

    __slots__ = 'data', 'player', 'track', 'threshold_ms'

    def __init__(self, data: dict) -> None:

        self.data: dict = data

        self.player: Protocol[Player] = data.get('player')
        self.track: str = data.get('track')

        self.threshold_ms: str = data.get('thresholdMs')

    def __repr__(self) -> str:
        return f'<slate.TrackStuckEvent player={self.player} track=\'{self.track}\' threshold_ms=\'{self.threshold_ms}\''

    def __str__(self) -> str:
        return 'track_stuck'


class WebSocketClosedEvent:

    __slots__ = 'data', 'player', 'track', 'reason', 'code', 'by_remote'

    def __init__(self, data: dict) -> None:

        self.data: dict = data

        self.player: Protocol[Player] = data.get('player')
        self.reason: str = data.get('reason')
        self.code: str = data.get('code')
        self.by_remote: str = data.get('byRemote')

    def __repr__(self) -> str:
        return f'<slate.WebSocketClosedEvent player={self.player} reason=\'{self.reason}\' code=\'{self.code}\' by_remote=\'{self.by_remote}\''

    def __str__(self) -> str:
        return 'websocket_closed'
