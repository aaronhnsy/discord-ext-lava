from typing import Literal, TypedDict

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
type StatsPayload = StatsData

############
# Event OP #
############
type EventPayload = EventData

###########
# Payload #
###########
type Payload = ReadyPayload | PlayerUpdatePayload | StatsPayload | EventPayload
