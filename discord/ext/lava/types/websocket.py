from typing import Literal, TypeAlias, TypedDict

from typing_extensions import NotRequired

from ..objects.types.events import EventData
from ..objects.types.stats import StatsData


# Ready OP

class ReadyData(TypedDict):
    op: Literal["ready"]
    resumed: bool
    sessionId: str


# Player Update OP

class PlayerStateData(TypedDict):
    time: int
    position: NotRequired[int]
    connected: bool
    ping: int


class PlayerUpdateData(TypedDict):
    op: Literal["playerUpdate"]
    guildId: str
    state: PlayerStateData


# Payloads

Payload: TypeAlias = ReadyData | PlayerUpdateData | StatsData | EventData
