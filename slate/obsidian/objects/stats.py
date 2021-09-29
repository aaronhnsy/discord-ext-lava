# Future
from __future__ import annotations

# Standard Library
from typing import Any


__all__ = (
    "ObsidianStats",
)


class ObsidianStats:

    def __init__(
        self,
        data: dict[str, Any]
    ) -> None:

        memory = data.get("memory", {})
        heap_used = memory.get("heap_used", {})
        non_heap_used = memory.get("non_heap_used", {})

        self.heap_used_init = heap_used.get("init")
        self.heap_used_max = heap_used.get("max")
        self.heap_used_committed = heap_used.get("committed")
        self.heap_used_used = heap_used.get("used")

        self.non_heap_used_init = non_heap_used.get("init")
        self.non_heap_used_max = non_heap_used.get("max")
        self.non_heap_used_committed = non_heap_used.get("committed")
        self.non_heap_used_used = non_heap_used.get("used")

        cpu = data.get("cpu", {})
        self.cpu_cores = cpu.get("cores")
        self.cpu_system_load = cpu.get("system_load")
        self.cpu_process_load = cpu.get("process_load")

        threads = data.get("threads", {})
        self.threads_running = threads.get("running")
        self.threads_daemon = threads.get("daemon")
        self.threads_peak = threads.get("peak")
        self.threads_total_started = threads.get("total_started")

        # TODO: Process the frames lost per guild; Separate object perhaps?

        players = data.get("players", {})
        self.players_active = players.get("active")
        self.players_total = players.get("total")

    def __repr__(self) -> str:
        return f"<slate.ObsidianStats total_players={self.players_total}, playing_active={self.players_active}>"
