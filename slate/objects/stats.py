

__all__ = ('LavalinkStats', 'AndesiteStats', 'Metadata')


class LavalinkStats:
    """
    A collection of Lavalink stats sent by :resource:`lavalink <lavalink>` every 30 or so seconds, and from :resource:`andesite <andesite>` when using the
    :resource:`lavalink <lavalink>` compatible websocket.
    """

    __slots__ = 'node', 'data', 'playing_players', 'total_players', 'uptime', 'memory_reservable', 'memory_allocated', 'memory_used', 'memory_free', 'system_load', \
                'lavalink_load', 'cpu_cores', 'frames_sent', 'frames_nulled', 'frames_deficit'

    def __init__(self, data: dict) -> None:

        self.data = data

        self.playing_players = data.get('playingPlayers')
        self.total_players = data.get('players')
        self.uptime = data.get('uptime')

        memory = data.get('memory', {})
        self.memory_reservable = memory.get('reservable', 0)
        self.memory_allocated = memory.get('allocated', 0)
        self.memory_used = memory.get('used', 0)
        self.memory_free = memory.get('free', 0)

        cpu = data.get('cpu', {})
        self.lavalink_load = cpu.get('lavalinkLoad', 0)
        self.system_load = cpu.get('systemLoad', 0)
        self.cpu_cores = cpu.get('cores', 0)

        frame_stats = data.get('frameStats', {})
        self.frames_deficit = frame_stats.get('deficit', -1)
        self.frames_nulled = frame_stats.get('nulled', -1)
        self.frames_sent = frame_stats.get('sent', -1)

    def __repr__(self) -> str:
        return f'<slate.LavalinkStats total_players={self.total_players} playing_players={self.playing_players} uptime={self.uptime}>'


class AndesiteStats:
    """
    A collection of stats sent by :resource:`andesite <andesite>` upon request using :py:meth:`AndesiteNode.request_andesite_stats`.
    """

    __slots__ = 'data', 'playing_players', 'total_players', 'uptime', 'runtime_pid', 'runtime_management_spec_version', 'runtime_name', 'vm_name', 'vm_vendor', 'vm_version', \
                'spec_name', 'spec_vendor', 'spec_version', 'processors', 'os_name', 'os_arch', 'os_version', 'cpu_andesite', 'cpu_system'

    def __init__(self, data: dict) -> None:

        self.data = data

        players = data.get('players')
        self.playing_players = players.get('playing')
        self.total_players = players.get('total')

        runtime = data.get('runtime')
        self.uptime = runtime.get('uptime')
        self.runtime_pid = runtime.get('pid')
        self.runtime_management_spec_version = runtime.get('managementSpecVersion')
        self.runtime_name = runtime.get('name')

        vm = runtime.get('vm')
        self.vm_name = vm.get('name')
        self.vm_vendor = vm.get('vendor')
        self.vm_version = vm.get('version')

        spec = runtime.get('spec')
        self.spec_name = spec.get('name')
        self.spec_vendor = spec.get('vendor')
        self.spec_version = spec.get('version')

        os = data.get('os')
        self.processors = os.get('processors')
        self.os_name = os.get('name')
        self.os_arch = os.get('arch')
        self.os_version = os.get('version')

        cpu = data.get('cpu')
        self.cpu_andesite = cpu.get('andesite')
        self.cpu_system = cpu.get('system')

        # TODO Add memory stats here maybe.

    def __repr__(self) -> str:
        return f'<slate.AndesiteStats total_players={self.total_players} playing_players={self.playing_players} uptime={self.uptime}>'


class Metadata:
    """
    Metadata sent by :resource:`andesite <andesite>` upon connection to the websocket.
    """

    __slots__ = 'data', 'version', 'version_major', 'version_minor', 'version_revision', 'version_commit', 'version_build', 'node_region', 'node_id', 'enabled_sources', \
                'loaded_plugins'

    def __init__(self, data: dict) -> None:

        self.data = data

        self.version = data.get('version')
        self.version_major = data.get('versionMajor')
        self.version_minor = data.get('versionMinor')
        self.version_revision = data.get('versionRevision')
        self.version_commit = data.get('versionCommit')
        self.version_build = data.get('versionBuild')
        self.node_region = data.get('nodeRegion')
        self.node_id = data.get('nodeId')
        self.enabled_sources = data.get('enabledSources')
        self.loaded_plugins = data.get('loadedPlugins')

    def __repr__(self) -> str:
        return f'<slate.Metadata version=\'{self.version}\' region=\'{self.node_region}\' id=\'{self.node_id}\' enabled_sources=\'{self.enabled_sources}\'>'
