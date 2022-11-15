from ..types.payloads import StatsPayload


__all__ = (
    "Stats",
)


class Stats:

    def __init__(self, data: StatsPayload) -> None:
        self.players = data["players"]
        self.playing_players = data["playingPlayers"]
        self.uptime = data["uptime"]

        memory = data["memory"]
        self.memory_free = memory["free"]
        self.memory_used = memory["used"]
        self.memory_allocated = memory["allocated"]
        self.memory_reservable = memory["reservable"]

        cpu = data["cpu"]
        self.cpu_cores = cpu["cores"]
        self.system_load = cpu["systemLoad"]
        self.lavalink_load = cpu["lavalinkLoad"]

        frame_stats = data["frameStats"] or {}
        self.frames_sent = frame_stats.get("sent", -1)
        self.frames_nulled = frame_stats.get("nulled", -1)
        self.frames_deficit = frame_stats.get("deficit", -1)

    def __repr__(self) -> str:
        return f"<discord.ext.lava.objects.Stats players={self.players}, playing_players={self.playing_players}>"
