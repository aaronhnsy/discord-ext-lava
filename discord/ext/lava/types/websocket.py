from typing import Literal, TypeAlias, TypedDict

from .common import PlayerStateData
from .objects.events import EventData
from .objects.stats import StatsData


############
# Ready OP #
############
class ReadyPayload(TypedDict):
    op: Literal["ready"]
    resumed: bool
    sessionId: str


####################
# Player Update OP #
####################
class PlayerUpdatePayload(TypedDict):
    op: Literal["playerUpdate"]
    guildId: str
    state: PlayerStateData


############
# Stats OP #
############
StatsPayload: TypeAlias = StatsData

############
# Event OP #
############
EventPayload: TypeAlias = EventData

###########
# Payload #
###########
Payload: TypeAlias = ReadyPayload | PlayerUpdatePayload | StatsPayload | EventPayload
