![](slate.jpg)

A [Lavalink](https://github.com/Frederikam/Lavalink/) [Andesite](https://github.com/natanbc/andesite) and [Obsidian](https://github.com/mixtape-bot/obsidian) compatible python wrapper for use with the commands extension of [discord.py](https://github.com/Rapptz/discord.py).

# Support
Support for using Slate can be found in my [discord server](https://discord.com/invite/xP8xsHr), or by opening an issue on this GitHub.

# Documentation
Slate uses [readthedocs.org](https://readthedocs.org/). The latest versions documentation can be found [here](https://slate-py.readthedocs.io/en/latest/) and previous versions can be viewed by clicking the banner at the bottom of the sidebar on the main documentation page.

# Installation
At the moment Slate is not on PyPi however it can be installed from git.

#### Please note that Slate requires python 3.7 or higher.
```shell
pip install -U git+https://github.com/Axelancerr/Slate
```

# Example
```python

import slate
import discord
import yarl

from discord.ext import commands

class MyBot(commands.Bot):
    
    def __init__(self) -> None:
        super().__init__(command_prefix='!', intents=discord.Intents().all(), 
                         activity=discord.Activity(type=discord.ActivityType.listening, name='to music!'))
        
        self.first_ready = True
        
        self.add_cog(Music(self))
        
    async def on_ready(self) -> None:
        
        if not self.first_ready:
            return
        
        await self.cogs["Music"].load()
        self.first_ready = False
     
        
class Music(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot = bot
        
        self.slate = slate.Client(bot=self.bot)
    
    async def load(self):
        await self.slate.create_node(host='127.0.0.1', port='20000', 
                                     password='secure password', identifier='ALPHA', 
                                     cls=slate.AndesiteNode)
        
    @commands.command(name='join', aliases=['connect'])
    async def join(self, ctx, *, channel: discord.TextChannel = None) -> None:
        
        if not channel:
            channel = getattr(ctx.author.voice, 'channel', None)
            if not channel:
                raise commands.CheckFailure('You must be in a voice channel to use this command'
                                            'without specifying the channel argument.')

        await self.slate.create_player(channel=channel, node_identifier='ALPHA')
        await ctx.send(f'Joined the voice channel `{channel}`')
        
    @commands.command(name='play')
    async def play(self, ctx, *, search: str) -> None:
        
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        
        url = yarl.URL(search)
        if not url.scheme or not url.host:
            if search.startswith('soundcloud'):
                search = f'scsearch:{search}'
            else:
                search = f'ytsearch:{search}'
                
        node = self.slate.get_node(identifier='ALPHA')
        results = await node.search(query=search)
        
        if not results:
            raise commands.CommandError('No tracks for playlists were found for that search term.')
        
        if isinstance(results, slate.Playlist):
            await ctx.voice_client.play(track=results.tracks[0])
        else:
            await ctx.voice_client.play(track=results[0])

```
