from __future__ import annotations

import logging
import time
from abc import ABC
from typing import List, Optional, Protocol, TYPE_CHECKING

import discord
from discord import VoiceProtocol

from slate.andesite.node import AndesiteNode
from slate.lavalink.node import LavalinkNode
from slate.objects import events

if TYPE_CHECKING:
    from slate.objects.track import Track
    from slate.objects.filters import Filter
    from slate import NodeType


__log__ = logging.getLogger('slate.bases.player')


class Player(VoiceProtocol, ABC):
    """
    A class that manages the playback of tracks within a discord channel.

    Parameters
    ----------
    client: :py:class:`typing.Protocol` [ :py:class:`discord.Client` ]
        The bot instance that this client should be connected to.
    channel: :py:class:`discord.VoiceChannel`
        The voice channel that this player should connect to.
    """

    def __init__(self, client: Protocol[discord.Client], channel: discord.VoiceChannel) -> None:
        super().__init__(client=client, channel=channel)

        self.client: Protocol[discord.Client] = client
        self._bot: Protocol[discord.Client] = self.client
        self.channel: Optional[discord.VoiceChannel] = channel
        self._guild: discord.Guild = channel.guild

        self._node: Optional[NodeType] = None
        self._current: Optional[Track] = None
        self._filter: Optional[Filter] = None
        self._volume: int = 100
        self._paused: bool = False
        self._connected: bool = False

        self._last_position: int = 0
        self._last_update: int = 0
        self._last_time: int = 0

        self._session_id: Optional[str] = None
        self._voice_server_update_data: Optional[dict] = None

    def __repr__(self) -> str:
        return f'<slate.Player client={self.client} channel={self.channel!r} is_connected={self.is_connected} is_paused={self.is_paused} is_playing={self.is_playing}>'

    #

    @property
    def bot(self) -> Protocol[discord.Client]:
        """
        :py:class:`typing.Protocol` [ :py:class:`discord.Client` ]:
            The bot instance that this player is connected to.
        """
        return self._bot

    @property
    def guild(self) -> discord.Guild:
        """
        :py:class:`discord.Guild`:
            The guild that this player is connected to.
        """
        return self._guild

    #

    @property
    def node(self) -> Optional[NodeType]:
        """
        Optional [ :py:class:`typing.Protocol` [ :py:class:`Node` ] ]:
            The node that is managing this player.
        """
        return self._node

    #

    @property
    def current(self) -> Optional[Track]:
        """
        Optional [ :py:class:`Track` ]:
            The track that this player is currently playing. Could be None if nothing is playing.
        """
        return self._current

    @property
    def filter(self) -> Optional[Filter]:
        """
        Optional [ :py:class:`Filter` ]:
            The filter currently set on this player. Could be None if one has not been set yet.
        """
        return self._filter

    @property
    def volume(self) -> int:
        """
        :py:class:`int`:
            The volume of the player.
        """
        return self._volume

    @property
    def is_paused(self) -> bool:
        """
        :py:class:`bool`:
            Whether or not the player is paused.
        """
        return self._paused

    @property
    def is_connected(self) -> bool:
        """
        :py:class:`bool`:
            Whether or not the player is connected to its voice channel.
        """
        return self.channel is not None

    @property
    def is_playing(self) -> bool:
        """
        :py:class:`bool`:
            Whether or not the player is connected and playing a track.
        """
        return self.is_connected and self._current is not None

    @property
    def position(self) -> float:
        """
        :py:class:`float`:
            The position of the current track. Will be 0 if nothing is playing.
        """

        if not self.is_playing or not self.current:
            return 0

        if self._paused:
            return min(self._last_position, self.current.length)

        position = self._last_position + ((time.time() * 1000) - self._last_update)

        if position > self.current.length:
            return 0

        return min(position, self.current.length)

    @property
    def listeners(self) -> List[discord.Member]:
        """
        :py:class:`List` [ :py:class:`discord.Member` ]:
            A list of members in the player's voice channel who are not bots and who are not deafened.
        """
        return [member for member in self.channel.members if not member.bot and not member.voice.deaf or not member.voice.self_deaf]

    #

    async def on_voice_server_update(self, data: dict) -> None:
        """
        :meta private:
        """

        __log__.debug(f'PLAYER | Received VOICE_SERVER_UPDATE | Data: {data}')

        self._voice_server_update_data = data
        await self._dispatch_voice_update()

    async def on_voice_state_update(self, data: dict) -> None:
        """
        :meta private:
        """

        __log__.debug(f'PLAYER | Received VOICE_STATE_UPDATE | Data: {data}')

        if not (channel_id := data.get('channel_id')):
            self.channel = None
            self._session_id = None
            self._voice_server_update_data = None
            return

        self.channel = self.guild.get_channel(int(channel_id))
        self._session_id = data.get('session_id', None)
        await self._dispatch_voice_update()

    async def _dispatch_voice_update(self) -> None:

        if not self._session_id or not self._voice_server_update_data:
            return

        op = 'voice-server-update' if isinstance(self.node, AndesiteNode) else 'voiceUpdate'
        await self.node._send(op=op, guildId=str(self.guild.id), sessionId=self._session_id, event=self._voice_server_update_data)

    async def _update_state(self, state: dict) -> None:

        __log__.info(f'PLAYER | Updating player state. | State: {state}')

        self._last_update = time.time() * 1000

        self._last_time = state.get('time', 0)
        self._last_position = state.get('position', 0)

        if isinstance(self.node, LavalinkNode):
            self._connected = state.get('connected', False)
        elif isinstance(self.node, AndesiteNode):
            self._paused = state.get('paused', False)
            self._volume = state.get('volume', 100)
            # self._filter = state.get('filters', Filter())

    def _dispatch_event(self, data: dict) -> None:

        event = getattr(events, data.get('type'), None)
        if not event:
            __log__.error(f'PLAYER | Unknown event type received. | Data: {data} ')
            return

        __log__.info(f'PLAYER | Dispatching {data.get("type")} event. | Data: {data}')

        data['player'] = self
        event = event(data=data)

        self.bot.dispatch(f'slate_{str(event)}', event)

    #

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        """
        Connects this player to it's voice channel.

        Parameters
        ----------
        timeout: float
            Unused, required by discord.py.
        reconnect: bool
            Unused, required by discord.py.
        """

        await self.guild.change_voice_state(channel=self.channel)
        __log__.info(f'PLAYER | Guild player \'{self.guild.id}\' joined channel \'{self.channel.id}\'.')

    async def stop(self, *, force: bool = False) -> None:
        """
        Stops the current track.

        ..  note::
            Sets :py:attr:`Player.current` to None

        Parameters
        ----------
        force: bool
            If True, a stop request will be sent to the websocket regardless of if :py:attr:`Player.current` is None.
        """

        if not self.current and not force:
            return

        await self.node._send(op='stop', guildId=str(self.guild.id))
        __log__.info(f'PLAYER | Guild player \'{self.guild.id}\' ended the current track.')

        self._current = None

    async def disconnect(self, *, force: bool = False) -> None:
        """
        Disconnects this player from it's voice channel.

        Parameters
        ----------
        force: bool
            If True, the player will try to disconnect regardless of if :py:attr:`Player.is_connected` is False.
        """

        if not self.is_connected and not force:
            return

        await self.guild.change_voice_state(channel=None)
        __log__.info(f'PLAYER | Guild player \'{self.guild.id}\' disconnected from voice channel \'{self.channel.id}\'.')

        self.cleanup()
        self.channel = None

    async def destroy(self, *, force: bool = False) -> None:
        """
        Calls :py:meth:`Player.disconnect` then sends a request to stop the current track and destroy the player.

        ..  note::
            This method removes the player from its node.

        Parameters
        ----------
        force: bool
            Passed to :py:meth:`Player.disconnect` and :py:meth:`Player.stop`
        """

        await self.disconnect(force=force)

        if self.node.is_connected:
            await self.stop(force=force)
            await self.node._send(op='destroy', guildId=str(self.guild.id))

        del self.node.players[self.guild.id]
        __log__.info(f'PLAYER | Guild player \'{self.guild.id}\' was destroyed.')

    async def play(self, track: Track, *, start: int = 0, end: int = 0, volume: int = None, no_replace: bool = False, pause: bool = False) -> None:
        """
        Plays a track.

        Parameters
        ----------
        track: :py:class:`Track`
            The track to be played.
        start: int
            The start position of the track in milliseconds.
        end: int
            The end position of the track in milliseconds.
        volume: int
            The starting volume of the track.
        no_replace: bool
            If True and :py:attr:`Player.current` is not None, this operation will be ignored.
        pause: bool
            Whether or not to start the track with playback paused.
        """

        self._last_position = 0
        self._last_time = 0
        self._last_update = 0

        payload = {
            'op': 'play',
            'guildId': str(self.guild.id),
            'track': str(track.track_id),
        }
        if 0 < start < track.length:
            payload['startTime'] = start
        if 0 < end < track.length:
            payload['endTime'] = end
        if volume:
            payload['volume'] = volume
        if no_replace:
            payload['noReplace'] = no_replace
        if pause:
            payload['pause'] = pause

        await self.node._send(**payload)
        self._current = track

        __log__.info(f'PLAYER | Player for guild \'{self.guild.id}\' is playing the track {self._current!r}.')

    async def set_filter(self, filter_instance: Filter) -> None:
        """
        Sets a filter on the player.

        Parameters
        ----------
        filter_instance: :py:class:`Filter`
            An instance of a filter object.
        """

        await self.node._send(op='filters', guildId=str(self.guild.id), **filter_instance._payload)
        self._filter = filter_instance

        __log__.info(f'PLAYER | Guild player \'{self.guild.id}\' is using the filter {self._filter!r}')

    async def set_volume(self, volume: int) -> None:
        """
        Sets the players volume.

        Parameters
        ----------
        volume: int
            The volume to set the player to.
        """

        await self.node._send(op='volume', guildId=str(self.guild.id), volume=volume)
        self._volume = volume

        __log__.info(f'PLAYER | Guild player \'{self.guild.id}\' volume is now {self._volume}.')

    async def set_pause(self, pause: bool) -> None:
        """
        Pauses or unpauses the player.

        Parameters
        ----------
        pause: bool
            True to pause the player, False to resume.
        """

        await self.node._send(op='pause', guildId=str(self.guild.id), pause=pause)
        self._paused = pause

        __log__.info(f'PLAYER | Guild player \'{self.guild.id}\' has set it\'s paused status to {self._paused}.')

    async def set_position(self, position: int) -> None:
        """
        Set the position of the player.

        Parameters
        ----------
        position: int
            The position to set the player to, in milliseconds.
        """

        if not self.current:
            return

        if 0 > position > self.current.length:
            return

        await self.node._send(op='seek', guildId=str(self.guild.id), position=position)
        __log__.info(f'PLAYER | Guild player \'{self.guild.id}\' has set it\'s position to {self.position}.')
