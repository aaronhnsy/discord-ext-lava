from typing import Literal, TypeAlias, TypedDict

from typing_extensions import NotRequired

from .objects.events import EventData
from .objects.stats import StatsData


# Ready OP

class ReadyData(TypedDict):
    op: Literal["ready"]
    resumed: bool
    sessionId: str


# Player Update OP

class PlayerUpdateStateData(TypedDict):
    time: int
    position: NotRequired[int]
    connected: bool
    ping: int


class PlayerUpdateData(TypedDict):
    op: Literal["playerUpdate"]
    guildId: str
    state: PlayerUpdateStateData


# Payloads

Payload: TypeAlias = ReadyData | PlayerUpdateData | StatsData | EventData
