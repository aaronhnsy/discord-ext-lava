import aiohttp
import discord
from discord.ext import commands, lava
from discord.utils import MISSING


type Lavalink = lava.Link["MyPlayer"]


class MyPlayer(lava.Player["CD"]):
    pass


class MyContext(commands.Context["CD"]):
    pass


class CD(commands.Bot):

    def __init__(self) -> None:
        super().__init__(
            intents=discord.Intents.all(),
            command_prefix=commands.when_mentioned_or("cb "),
        )
        self.session: aiohttp.ClientSession = discord.utils.MISSING
        self.lavalink: Lavalink = discord.utils.MISSING

    async def get_context(
        self,
        message: discord.Message | discord.Interaction,
        *,
        cls: type[commands.Context["CD"]] = MISSING
    ) -> commands.Context["CD"]:
        return await super().get_context(message, cls=MyContext)

    async def _connect_lavalink(self) -> None:
        lavalink: Lavalink = lava.Link(
            host="",
            port=12345,
            password="",
            user_id=self.user.id,  # pyright: ignore
            spotify_client_id="",
            spotify_client_secret="",
        )
        await lavalink.connect()
        self.lavalink = lavalink

    async def setup_hook(self) -> None:
        await self._connect_lavalink()
