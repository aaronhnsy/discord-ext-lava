from typing import Literal, TypedDict


class MemoryStatsData(TypedDict):
    free: int
    used: int
    allocated: int
    reservable: int


class CPUStatsData(TypedDict):
    cores: int
    systemLoad: float
    lavalinkLoad: float


class FrameStatsData(TypedDict):
    sent: int
    nulled: int
    deficit: int


class StatsData(TypedDict):
    op: Literal["stats"]
    players: int
    playingPlayers: int
    uptime: int
    memory: MemoryStatsData
    cpu: CPUStatsData
    frameStats: FrameStatsData | None
