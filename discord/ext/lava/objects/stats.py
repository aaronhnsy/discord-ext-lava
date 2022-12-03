from ..types import CPUStatsData, FrameStatsData, MemoryStatsData, StatsPayload


__all__ = (
    "Stats",
)


class Stats:

    def __init__(self, data: StatsPayload) -> None:
        self.players: int = data["players"]
        self.playing_players: int = data["playingPlayers"]
        self.uptime: int = data["uptime"]

        memory: MemoryStatsData = data["memory"]
        self.memory_free: int = memory["free"]
        self.memory_used: int = memory["used"]
        self.memory_allocated: int = memory["allocated"]
        self.memory_reservable: int = memory["reservable"]

        cpu: CPUStatsData = data["cpu"]
        self.cpu_cores: int = cpu["cores"]
        self.system_load: float = cpu["systemLoad"]
        self.lavalink_load: float = cpu["lavalinkLoad"]

        frame_stats: FrameStatsData | dict[str, int] = data["frameStats"] or {}
        self.frames_sent: int = frame_stats.get("sent", -1)
        self.frames_nulled: int = frame_stats.get("nulled", -1)
        self.frames_deficit: int = frame_stats.get("deficit", -1)

    def __repr__(self) -> str:
        return f"<discord.ext.lava.objects.Stats players={self.players}, playing_players={self.playing_players}>"
