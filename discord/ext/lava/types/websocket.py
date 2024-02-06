from typing import Literal, TypedDict

from .common import PlayerStateData
from .objects.events import EventData
from .objects.stats import StatsData


# 'ready' payload
class ReadyPayload(TypedDict):
    op: Literal["ready"]
    resumed: bool
    sessionId: str


# 'playerUpdate' payload
class PlayerUpdatePayload(TypedDict):
    op: Literal["playerUpdate"]
    guildId: str
    state: PlayerStateData


# 'stats' payload
class StatsPayload(StatsData):
    op: Literal["stats"]


# 'event' payload
type EventPayload = EventData

# payload
type Payload = ReadyPayload | PlayerUpdatePayload | StatsPayload | EventPayload
