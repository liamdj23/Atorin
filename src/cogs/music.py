import itertools

import discord
from discord.ext import commands
import youtube_dl
import time
from youtube_search import YoutubeSearch
from asyncio import TimeoutError
from async_timeout import timeout
import asyncio

ytdl_options = {
    "format": "bestaudio[ext=m4a]",
    "outtmpl": "../songs/%(id)s.%(ext)s"
}

ytdl = youtube_dl.YoutubeDL(ytdl_options)


class Player:
    def __init__(self, ctx):
        self.ctx = ctx
        self.guild = ctx.guild
        self.next = asyncio.Event()
        self.queue = asyncio.Queue()
        self.now_playing = None
        self.source = None
        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        await self.ctx.bot.wait_until_ready()
        while not self.ctx.bot.is_closed():
            self.next.clear()
            try:
                async with timeout(300):
                    song = await self.queue.get()
            except TimeoutError:
                await self.ctx.send("🥺 **Rozłączono** z powodu długiej nieaktywności.")
                return self.destroy(self.guild)
            self.now_playing = song
            file = discord.FFmpegPCMAudio("../songs/{}.m4a".format(song["id"]))
            self.source = discord.PCMVolumeTransformer(file, volume=1.0)
            self.guild.voice_client.play(self.source,
                                         after=lambda e: self.ctx.bot.loop.call_soon_threadsafe(self.next.set))
            embed = self.ctx.bot.embed(self.ctx.author)
            embed.title = "Teraz odtwarzane"
            embed.add_field(name="🎧 Utwór", value=song["title"], inline=False)
            embed.add_field(name="🛤️ Długość", value=time.strftime("%H:%M:%S", time.gmtime(song["duration"])))
            embed.add_field(name="💃 Zaproponowany przez", value=self.ctx.author.mention)
            embed.set_thumbnail(url=song["thumbnail"])
            await self.ctx.send(embed=embed)

            await self.next.wait()

            self.now_playing = None
            self.source.cleanup()
            self.source = None

    def destroy(self, guild):
        return self.ctx.bot.loop.create_task(self.ctx.cog.cleanup(guild))


class Music(commands.Cog, name="🎵 Muzyka (beta)"):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass
        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = Player(ctx)
            self.players[ctx.guild.id] = player
        return player

    @commands.command(
        description="Odtwarza muzykę na kanale głosowym\n\nPrzykłady użycia:"
                    "\n&play despacito\n&play https://www.youtube.com/watch?v=kJQP7kiw5Fk",
        usage="<tytuł lub link do Youtube>",
        aliases=["p"]
    )
    @commands.guild_only()
    async def play(self, ctx, *, song):
        if not ctx.author.voice:
            await ctx.send("❌ Musisz być połączony do kanału głosowego!")
            return
        voice_channel = ctx.author.voice.channel
        voice = ctx.guild.voice_client
        searching = await ctx.send("🔎 Trwa wyszukiwanie utworu...")
        try:
            results = YoutubeSearch(song, max_results=5).to_dict()
        except KeyError:
            results = YoutubeSearch(song, max_results=5).to_dict()
        if not results:
            await ctx.send("❌ Nie znaleziono utworów o podanej nazwie.")
            return
        embed = self.bot.embed(ctx.author)
        embed.title = "Wyniki wyszukiwania"
        embed.description = "❓ **Napisz cyfrę odpowiadającą utworowi, którego szukasz.**\n\n"
        i = 0
        for result in results:
            i = i + 1
            embed.description += "**#{}**. {} ({})\n".format(
                i, result["title"], result["duration"]
            )
        await searching.edit(content=None, embed=embed)

        def check(message):
            return message.author == ctx.author and message.content.isdigit() and not int(message.content) > 5

        try:
            choice = await self.bot.wait_for("message", check=check, timeout=60)
        except TimeoutError:
            await searching.edit(embed=None, content="🔇 Nie wybrano utworu.")
            return
        choice = int(choice.content) - 1
        await searching.edit(content="✅ Wybrano **#{}**. **{}** ({}).".format(
            choice + 1, results[choice]["title"], results[choice]["duration"]
        ), embed=None)
        metadata = ytdl.extract_info("https://www.youtube.com/watch?v=" + results[choice]["id"], download=False)
        if metadata["filesize"] > 15000000:
            await ctx.send("❌ Rozmiar podanego utworu jest za duży.")
            return
        ytdl.download(["https://www.youtube.com/watch?v=" + results[choice]["id"]])
        if not voice:
            voice = await voice_channel.connect()
        player = self.get_player(ctx)
        await player.queue.put(metadata)
        if voice.is_playing():
            await ctx.send("📩 Utwór **{}** został dodany do kolejki.".format(metadata["title"]))

    @commands.command(
        description="Wstrzymuje odtwarzanie muzyki",
        aliases=["zatrzymaj"]
    )
    @commands.guild_only()
    async def pause(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Musisz być połączony do kanału głosowego!")
            return
        voice = ctx.guild.voice_client
        if voice and voice.is_playing():
            voice.pause()
            await ctx.send("⏸ Wstrzymano odtwarzanie. Aby wznowić wpisz `&resume`.")
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Wznawia odtwarzanie muzyki",
        aliases=["wznów", "wznow"]
    )
    @commands.guild_only()
    async def resume(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Musisz być połączony do kanału głosowego!")
            return
        voice = ctx.guild.voice_client
        if voice and voice.is_paused():
            voice.resume()
            await ctx.send("▶️Wznowiono odtwarzanie.")
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Zatrzymuje odtwarzanie muzyki"
    )
    @commands.guild_only()
    async def stop(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Musisz być połączony do kanału głosowego!")
            return
        voice = ctx.guild.voice_client
        if voice and voice.is_playing():
            await self.cleanup(ctx.guild)
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Pomija aktualnie odtwarzany utwór",
        aliases=["pomiń", "pomin"]
    )
    @commands.guild_only()
    async def skip(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Musisz być połączony do kanału głosowego!")
            return
        voice = ctx.guild.voice_client
        if voice and voice.is_playing():
            voice.stop()
            await ctx.send("⏭️Pominięto utwór.")
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Ustawia głośność aktualnie odtwarzanego utworu",
        aliases=["głośność", "glosnosc"]
    )
    @commands.guild_only()
    async def volume(self, ctx, vol: int):
        if not ctx.author.voice:
            await ctx.send("❌ Musisz być połączony do kanału głosowego!")
            return
        voice = ctx.guild.voice_client
        if voice and voice.is_playing():
            player = self.get_player(ctx)
            source = player.source
            source.volume = float(vol/100)
            await ctx.send("🔉 Ustawiono glośność na {}%.".format(vol))
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Wyświetla kolejkę utworów do odtworzenia",
        aliases=["kolejka"]
    )
    @commands.guild_only()
    async def queue(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Musisz być połączony do kanału głosowego!")
            return
        voice = ctx.guild.voice_client
        if voice and voice.is_playing():
            player = self.get_player(ctx)
            if player.queue.empty():
                return await ctx.send('🕳️ Kolejka jest pusta!')

            upcoming = list(itertools.islice(player.queue._queue, 0, 5))

            fmt = '\n'.join(f'**{_["title"]}** ({time.strftime("%H:%M:%S", time.gmtime(_["duration"]))})' for _ in upcoming)
            embed = self.bot.embed(ctx.author)
            embed.title = f"Utwory w kolejce: {len(upcoming)}"
            embed.description = fmt
            await ctx.send(embed=embed)
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Wyświetla aktualnie odtwarzany utwór",
        aliases=["np", "nowp"]
    )
    @commands.guild_only()
    async def nowplaying(self, ctx):
        player = self.get_player(ctx)
        song = player.now_playing
        embed = ctx.bot.embed(ctx.author)
        embed.title = "Teraz odtwarzane"
        embed.add_field(name="🎧 Utwór", value=song["title"], inline=False)
        embed.add_field(name="🛤️ Długość", value=time.strftime("%H:%M:%S", time.gmtime(song["duration"])))
        embed.add_field(name="💃 Zaproponowany przez", value=ctx.author.mention)
        embed.set_thumbnail(url=song["thumbnail"])
        await ctx.send(embed=embed)