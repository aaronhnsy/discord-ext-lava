from ..types.objects.stats import StatsData


__all__ = ["Stats"]


class Stats:
    __slots__ = (
        "players", "playing_players", "uptime", "memory_free", "memory_used", "memory_allocated",
        "memory_reservable", "cpu_cores", "system_load", "lavalink_load", "frames_sent", "frames_nulled",
        "frames_deficit",
    )

    def __init__(self, data: StatsData) -> None:
        # general
        self.players: int = data["players"]
        self.playing_players: int = data["playingPlayers"]
        self.uptime: int = data["uptime"]
        # memory
        memory = data["memory"]
        self.memory_free: int = memory["free"]
        self.memory_used: int = memory["used"]
        self.memory_allocated: int = memory["allocated"]
        self.memory_reservable: int = memory["reservable"]
        # cpu
        cpu = data["cpu"]
        self.cpu_cores: int = cpu["cores"]
        self.system_load: float = cpu["systemLoad"]
        self.lavalink_load: float = cpu["lavalinkLoad"]
        # frame stats
        frame_stats = data["frameStats"] or {}
        self.frames_sent: int = frame_stats.get("sent", -1)
        self.frames_nulled: int = frame_stats.get("nulled", -1)
        self.frames_deficit: int = frame_stats.get("deficit", -1)

    def __repr__(self) -> str:
        return f"<lava.{self.__class__.__name__}: players={self.players}, playing_players={self.playing_players}>"
