from typing import Any

from discord import VoiceProtocol


class LavalinkPlayer(VoiceProtocol):

    async def on_voice_server_update(self, data: dict[str, Any]) -> None:

        __log__.debug(f'PLAYER | Received VOICE_SERVER_UPDATE | Data: {data}')

        self._voice_server_update_data = data
        await self._dispatch_voice_update()

    async def on_voice_state_update(self, data: dict[str, Any]) -> None:

        __log__.debug(f'PLAYER | Received VOICE_STATE_UPDATE | Data: {data}')

        if not (channel_id := data.get('channel_id')):
            self.channel = None
            self._session_id = None
            self._voice_server_update_data = None
            return

        self.channel = self.guild.get_channel(int(channel_id))
        self._session_id = data.get('session_id')
        await self._dispatch_voice_update()

    async def connect(self, *, timeout: float = None, reconnect: bool = None) -> None:

        await self.guild.change_voice_state(channel=self.channel)
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' connected to voice channel \'{self.channel.id}\'.')

    async def disconnect(self, *, force: bool = False) -> None:

        if not self.is_connected and not force:
            return

        await self.guild.change_voice_state(channel=None)
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' disconnected from voice channel \'{self.channel.id}\'.')

        if self.node.is_connected:
            await self.stop(force=force)
            await self.node._send(op=Op.PLAYER_DESTROY, **{'guild_id': str(self.guild.id)})

        del self.node.players[self.guild.id]
        __log__.info(f'PLAYER | Player \'{self.guild.id}\' was destroyed.')

        self.cleanup()
#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#
