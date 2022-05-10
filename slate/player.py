# Future
from __future__ import annotations

# Standard Library
import logging
import time
from typing import Any, Generic

# Packages
import discord
import discord.types.voice

# Local
from .node import Node
from .objects.enums import Provider
from .objects.events import TrackEnd, TrackException, TrackStart, TrackStuck, WebsocketClosed, WebsocketOpen
from .objects.filters import Filter
from .objects.track import Track
from .pool import Pool
from .types import BotT, PlayerT, VoiceChannel
from .utils import MISSING


__all__ = (
    "Player",
)
__log__: logging.Logger = logging.getLogger("slate.player")


OBSIDIAN_EVENT_MAPPING: dict[str, Any] = {
    "WEBSOCKET_OPEN":   WebsocketOpen,
    "WEBSOCKET_CLOSED": WebsocketClosed,
    "TRACK_START":      TrackStart,
    "TRACK_END":        TrackEnd,
    "TRACK_STUCK":      TrackStuck,
    "TRACK_EXCEPTION":  TrackException,
}

LAVALINK_EVENT_MAPPING: dict[str, Any] = {
    "WebsocketClosedEvent": WebsocketClosed,
    "TrackStartEvent":      TrackStart,
    "TrackEndEvent":        TrackEnd,
    "TrackStuckEvent":      TrackStuck,
    "TrackExceptionEvent":  TrackException,
}


class Player(discord.VoiceProtocol, Generic[BotT, PlayerT]):

    def __init__(
        self,
        client: BotT = MISSING,
        channel: VoiceChannel = MISSING, /,
        *,
        node: Node[BotT, PlayerT] | None = None,
    ) -> None:
        """
        Parameters
        ----------
        node
            The node this player should be attached to, if :obj:`None` the player will be attached to the first node
            found from the pool.

        Warnings
        --------
            To connect to a voice channel you must construct an instance of this class, setting the ``node`` argument
            (and extras, if subclassing) but **not** the ``client`` or ``channel`` arguments. You can then pass it to
            the ``cls`` argument of :meth:`discord.abc.Connectable.connect`.
        """

        self.client: BotT = client
        self.channel: VoiceChannel = channel

        self._node: Node[BotT, PlayerT] = node or Pool.get_node()  # type: ignore

        self._voice_server_update_data: discord.types.voice.VoiceServerUpdate | None = None
        self._session_id: str | None = None

        self._current_track_id: str | None = None
        self._current: Track | None = None
        self._paused: bool = False

        self._last_update: float = 0
        self._position: float = 0
        self._timestamp: float = 0

        self._filter: Filter | None = None

    def __call__(
        self,
        client: discord.Client,
        channel: discord.abc.Connectable, /,
    ) -> PlayerT:

        self.client = client  # type: ignore
        self.channel = channel  # type: ignore

        self._node._players[channel.guild.id] = self  # type: ignore

        return self  # type: ignore

    def __repr__(self) -> str:
        return "<slate.Player>"

    # Discord.py abstract methods

    async def on_voice_server_update(
        self,
        data: discord.types.voice.VoiceServerUpdate
    ) -> None:

        __log__.debug(f"Player '{self.channel.guild.id}' received VOICE_SERVER_UPDATE.\nData: {data}")

        self._voice_server_update_data = data
        await self._dispatch_voice_update()

    async def on_voice_state_update(
        self,
        data: discord.types.voice.GuildVoiceState
    ) -> None:

        __log__.debug(f"Player '{self.channel.guild.id}' received VOICE_STATE_UPDATE.\nData: {data}")

        self._session_id = data.get("session_id")
        await self._dispatch_voice_update()

    async def _dispatch_voice_update(self) -> None:

        if not self._session_id or not self._voice_server_update_data:
            return

        if self._node.provider is Provider.OBSIDIAN:
            data = {
                "session_id": self._session_id,
                **self._voice_server_update_data
            }
        else:
            data = {
                "sessionId": self._session_id,
                "event":     self._voice_server_update_data,
            }

        await self._node._send_payload(
            0,  # voiceUpdate
            data=data,
            guild_id=str(self.channel.guild.id)
        )

    # Websocket

    def _dispatch_event(
        self,
        data: dict[str, Any]
    ) -> None:

        _type = data["type"]

        if not (event := OBSIDIAN_EVENT_MAPPING.get(_type) if self._node.provider is Provider.OBSIDIAN else LAVALINK_EVENT_MAPPING.get(_type)):
            __log__.error(f"Player '{self.channel.guild.id}' received an event with an unknown type '{_type}'.\nData: {data}")
            return

        event = event(data)

        __log__.info(f"Player '{self.channel.guild.id}' dispatched an event with type '{_type}'.\nData: {data}")
        self.bot.dispatch(f"slate_{event.type.lower()}", self, event)

    def _update_state(
        self,
        data: dict[str, Any]
    ) -> None:

        self._last_update = time.time() * 1000

        if self._node.provider is Provider.OBSIDIAN:

            current: dict[str, Any] = data["current_track"]
            self._current_track_id = current["track"]
            self._paused = current["paused"]
            self._position = current["position"]
            self._timestamp = data["timestamp"]
            # TODO: Parse filters from data["filters"]

        else:
            state: dict[str, Any] = data["state"]
            self._position = state.get("position", 0)
            self._timestamp = state["time"]

    # Properties

    @property
    def bot(self) -> BotT:
        """
        The bot this player is attached to.
        """
        return self.client

    @property
    def voice_channel(self) -> VoiceChannel:
        """
        The voice channel this player is connected to.
        """
        return self.channel

    @property
    def node(self) -> Node[BotT, PlayerT]:
        """
        The node this player is attached to.
        """
        return self._node

    @property
    def current_track_id(self) -> str | None:
        """
        The ID of the current track. This is :class:`None` if no track is playing.
        """
        return self._current_track_id

    @property
    def current(self) -> Track | None:
        """
        The current track. This is :class:`None` if no track is playing.
        """
        return self._current

    @property
    def paused(self) -> bool:
        """
        Whether the player is paused.
        """
        return self._paused

    @property
    def position(self) -> float:
        """
        The position of the player. Returns 0 if no track is playing.
        """

        if not self.is_playing():
            return 0

        assert self._current is not None

        if self._paused:
            return min(self._position, self._current.length)

        position = self._position + ((time.time() * 1000) - self._last_update)

        if position > self._current.length:
            return 0

        return position

    @property
    def filter(self) -> Filter | None:
        """
        The players current filter, if set.
        """
        return self._filter

    @property
    def listeners(self) -> list[discord.Member]:
        """
        A list of members in the players voice channel.

        Notes
        -----
        This only returns **non-bot** members who are **not** deafened.
        """
        return [member for member in getattr(self.channel, "members", []) if not member.bot and (not member.voice.deaf or not member.voice.self_deaf)]

    # Utility methods

    def is_connected(self) -> bool:
        """
        Returns :obj:`True` if the player is connected to its voice channel, :obj:`False` otherwise.
        """
        return self.channel is not None

    def is_playing(self) -> bool:
        """
        Returns :obj:`True` if the player is playing a track, :obj:`False` otherwise.
        """
        return self.is_connected() is True and self._current is not None

    def is_paused(self) -> bool:
        """
        Returns :obj:`True` if the player is paused, :obj:`False` otherwise.
        """
        return self._paused is True

    # Player methods

    async def connect(
        self,
        *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_mute: bool = False,
        self_deaf: bool = True,
    ) -> None:
        """
        Connects the player to its voice channel.

        Parameters
        ----------
        timeout
            Unused parameter, does nothing.
        reconnect
            Unused parameter, does nothing.
        self_mute
            :obj:`True` if the player should be muted when connected. Defaults to :obj:`False`.
        self_deaf
            :obj:`True` if the player should be deafened when connected. Defaults to :obj:`True`.
        """

        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)
        __log__.info(f"Player '{self.channel.guild.id}' connected to voice channel '{self.channel.id}'.")

    async def disconnect(
        self,
        *,
        force: bool = False
    ) -> None:
        """
        Disconnects the player from its voice channel and removed it from the node.

        Parameters
        ----------
        force
            :obj:`True` if the player should send a request to the provider server to stop the current track even if
            one is not playing. Defaults to :obj:`False`.
        """

        __log__.info(f"Player '{self.channel.guild.id}' disconnected from voice channel '{self.channel.id}'.")
        await self.channel.guild.change_voice_state(channel=None)

        if self._node.is_connected():

            await self.stop(force=force)
            await self._node._send_payload(
                11,  # destroy
                guild_id=str(self.channel.guild.id)
            )

        try:
            del self._node._players[self.channel.guild.id]
        except KeyError:
            pass

        self.cleanup()

    async def play(
        self,
        track: Track, /,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        no_replace: bool = False
    ) -> None:
        """
        Plays the given track.

        Parameters
        ----------
        track
            The track to play.
        start_time
            The start time of the track in milliseconds. Defaults to :obj:`None`.
        end_time
            The end time of the track in milliseconds. Defaults to :obj:`None`.
        no_replace
            :obj:`True` if this track should not replace the current track, if any. Defaults to :obj:`False`.
        """

        data: dict[str, Any] = {
            "track": track.id,
        }
        if self._node.provider is Provider.OBSIDIAN:
            if start_time:
                data["start_time"] = start_time
            if end_time:
                data["end_time"] = end_time
            if no_replace:
                data["no_replace"] = no_replace
        else:
            if start_time:
                data["startTime"] = start_time
            if end_time:
                data["endTime"] = end_time
            if no_replace:
                data["noReplace"] = no_replace

        await self._node._send_payload(
            6,  # play
            data=data,
            guild_id=str(self.channel.guild.id)
        )
        __log__.info(f"Player '{self.channel.guild.id}' started playing track '{track!r}'.")

        self._current_track_id = track.id
        self._current = track
        self._last_update = 0
        self._position = 0

    async def stop(
        self,
        *,
        force: bool = False
    ) -> None:
        """
        Stops the current track.

        Parameters
        ----------
        force
            :obj:`True` if the player should send the stop track request to the provider server even if this player's
            :attr:`~Player.current` attribute is :class:`None`. Defaults to :obj:`False`.
        """

        if self._current is None and not force:
            return

        await self._node._send_payload(
            7,  # stop
            guild_id=str(self.channel.guild.id)
        )
        __log__.info(f"Player '{self.channel.guild.id}' stopped playing track '{self.current!r}'.")

        self._current_track_id = None
        self._current = None
        self._last_update = 0
        self._position = 0

    async def set_pause(
        self,
        pause: bool, /,
    ) -> None:
        """
        Sets the players pause state.

        Parameters
        ----------
        pause
            :obj:`True` if the player should be paused, :obj:`False` otherwise.
        """

        await self._node._send_payload(
            8,  # pause
            data={"state": pause} if self._node.provider is Provider.OBSIDIAN else {"pause": pause},
            guild_id=str(self.channel.guild.id)
        )
        __log__.info(f"Player '{self.channel.guild.id}' set its paused state to '{pause}'.")

        self._paused = pause

    async def set_filter(
        self,
        filter: Filter, /,
        *,
        set_position: bool = True
    ) -> None:
        """
        Sets the players filter.

        Parameters
        ----------
        filter
            The filter to set.
        set_position
            :obj:`True` if the player should set its position to the current position which applied filters instantly.
            Defaults to :obj:`True`.
        """

        await self._node._send_payload(
            9,  # filters
            data={"filters": filter.payload} if self._node.provider is Provider.OBSIDIAN else filter.payload,
            guild_id=str(self.channel.guild.id)
        )
        __log__.info(f"Player '{self.channel.guild.id}' set its filter to '{filter!r}'.")

        self._filter = filter

        if set_position:
            await self.set_position(self.position)

    async def set_position(
        self,
        position: float, /,
        *,
        force: bool = False
    ) -> None:
        """
        Sets the players position.

        Parameters
        ----------
        position
            The position to set, in milliseconds.
        force
            :obj:`True` if the player should send the set position request to the provider server even if this player's
            :attr:`~Player.current` attribute is :class:`None`. Defaults to :obj:`False`.
        """

        if (self._current is None or 0 > position > self._current.length) and not force:
            return

        await self._node._send_payload(
            10,  # seek
            data={"position": round(position)},
            guild_id=str(self.channel.guild.id)
        )
        __log__.info(f"Player '{self.channel.guild.id}' set its position to '{self.position}'.")

        self._last_update = time.time() * 1000
        self._position = position
