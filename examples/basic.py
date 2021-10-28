# Future
from __future__ import annotations

# Packages
import discord
import yarl
from discord.ext import commands

# My stuff
import slate
import slate.obsidian


class MyBot(commands.Bot):

    def __init__(self) -> None:
        super().__init__(
            activity=discord.Activity(type=discord.ActivityType.listening, name="to music!"),
            intents=discord.Intents().all(),
            command_prefix=commands.when_mentioned_or(">"),
        )

    async def on_ready(self) -> None:

        print(f"{self.user.name} is ready!")
        await self.cogs["Music"].load()  # type: ignore


class Music(commands.Cog):

    def __init__(self, bot: MyBot) -> None:
        self.bot: MyBot = bot

        # Note: The type hint here is a TypeVar which tells the NodePool
        # which types it can expect certain attributes to be, this is
        # useful for static type checkers like pyright when you are using
        # a custom bot, context, or player subclass.
        self.slate: slate.obsidian.NodePool[MyBot, commands.Context, slate.obsidian.Player] = slate.obsidian.NodePool()

    async def load(self) -> None:

        await self.slate.create_node(
            bot=self.bot,
            identifier="ObsidianNode01",
            host="127.0.0.1",
            port="3030",
            password="",
        )

        print("Slate is connected!")

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await ctx.send(str(error))

    @commands.command(name="join")
    async def join(self, ctx: commands.Context) -> None:

        # Check if a player already exists (for this guild) and if its connected to a voice channel.
        if ctx.voice_client and ctx.voice_client.is_connected():
            raise commands.CommandError(f"I am already connected to {ctx.voice_client.channel.mention}.")

        # Check if the author is in a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("You must be connected to a voice channel to use this command.")

        # Connect to the authors voice channel using the default slate obsidian player.
        await ctx.author.voice.channel.connect(cls=slate.obsidian.Player)  # type: ignore
        await ctx.send(f"Joined the voice channel {ctx.voice_client.channel.mention}.")

    @commands.command(name="play")
    async def play(self, ctx: commands.Context, *, search: str) -> None:

        # If a player doesnt exist, invoke the join command.
        if ctx.voice_client is None or ctx.voice_client.is_connected() is False:
            await ctx.invoke(self.join)

        # If the search parameter is a URL, you'll wanna specify the source as Source.NONE
        # because that'll just pass the link straight through to obsidian, if its not a url,
        # you'll probably want to set it to Source.YOUTUBE as that will make obsidian preform
        # a search with your query.
        url = yarl.URL(search)
        if url.scheme and url.host:
            source = slate.Source.NONE
        else:
            source = slate.Source.YOUTUBE

        # Searches can raise errors, so catch them and display a relevant error message.
        try:
            result = await ctx.voice_client._node.search(search, source=source, ctx=ctx)
        except slate.NoResultsFound:
            raise commands.CommandError("No results were found for your search.")
        except slate.HTTPError:
            raise commands.CommandError("There was an error while searching for results.")

        # Play the first track found in the search result.
        await ctx.voice_client.play(result.tracks[0])
        await ctx.send(f"Now playing: **{result.tracks[0].title}** by **{result.tracks[0].author}**")

    @commands.command(name="disconnect")
    async def disconnect(self, ctx: commands.Context) -> None:

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            raise commands.CommandError("I am not connected to any voice channels.")
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("You must be connected to a voice channel to use this command.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            raise commands.CommandError(f"You must be connected to {ctx.voice_client.channel.mention} to use this command.")

        await ctx.send(f"Left {ctx.voice_client.channel.mention}.")
        await ctx.voice_client.disconnect()


my_bot = MyBot()
my_bot.add_cog(Music(my_bot))
my_bot.run("TOKEN")
