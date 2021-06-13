"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any


__all__ = ['ObsidianStats']


class ObsidianStats:

    __slots__ = 'heap_used_init', 'heap_used_max', 'heap_used_committed', 'heap_used_used', 'non_heap_used_init', 'non_heap_used_max', 'non_heap_used_committed', 'non_heap_used_used', \
                'cpu_cores', 'cpu_system_load', 'cpu_process_load', 'threads_running', 'threads_daemon', 'threads_peak', 'threads_total_started', 'players_active', 'players_total'

    def __init__(self, data: dict[str, Any]) -> None:

        memory = data.get('memory')
        heap_used = memory.get('heap_used')
        non_heap_used = memory.get('non_heap_used')

        self.heap_used_init = heap_used.get('init')
        self.heap_used_max = heap_used.get('max')
        self.heap_used_committed = heap_used.get('committed')
        self.heap_used_used = heap_used.get('used')

        self.non_heap_used_init = non_heap_used.get('init')
        self.non_heap_used_max = non_heap_used.get('max')
        self.non_heap_used_committed = non_heap_used.get('committed')
        self.non_heap_used_used = non_heap_used.get('used')

        cpu = data.get('cpu')
        self.cpu_cores = cpu.get('cores')
        self.cpu_system_load = cpu.get('system_load')
        self.cpu_process_load = cpu.get('process_load')

        threads = data.get('threads')
        self.threads_running = threads.get('running')
        self.threads_daemon = threads.get('daemon')
        self.threads_peak = threads.get('peak')
        self.threads_total_started = threads.get('total_started')

        # TODO: Process the frames lost per guild; Separate object perhaps?

        players = data.get('players')
        self.players_active = players.get('active')
        self.players_total = players.get('total')

    def __repr__(self) -> str:
        return f'<slate.ObsidianStats total_players={self.players_total} playing_active={self.players_active}>'
