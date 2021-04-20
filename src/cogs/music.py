from youtubesearchpython.__future__ import VideosSearch

import itertools

import discord
from discord.ext import commands
import youtube_dl
import time
from asyncio import TimeoutError
from async_timeout import timeout
import asyncio
import os.path
from datetime import datetime

ytdl_options = {
    "format": "bestaudio[ext=m4a]",
    "outtmpl": "../songs/%(id)s.%(ext)s",
    "quiet": True
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
                async with timeout(600):
                    song = await self.queue.get()
            except TimeoutError:
                if self.guild.voice_client and not self.guild.voice_client.is_playing():
                    await self.ctx.send("🥺 **Rozłączono** z powodu długiej nieaktywności.")
                    self.destroy(self.guild)
                return
            self.now_playing = song
            file = discord.FFmpegPCMAudio("../songs/{}.m4a".format(song["id"]))
            self.source = discord.PCMVolumeTransformer(file, volume=1.0)
            self.guild.voice_client.play(self.source,
                                         after=lambda e: self.ctx.bot.loop.call_soon_threadsafe(self.next.set))
            embed = self.ctx.bot.embed(self.ctx.author)
            embed.title = "Teraz odtwarzane"
            embed.add_field(name="🎧 Utwór", value=song["title"], inline=False)
            embed.add_field(name="🛤️ Długość", value=song["duration"])
            embed.add_field(name="💃 Zaproponowany przez", value=song["requester"].mention)
            embed.set_thumbnail(url=song["thumbnails"][0]["url"])
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

    class MusicException(commands.CommandError):
        def __init__(self, message=None, *args):
            super().__init__(message, args)
            self.original = message

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

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if guild_check:
            should_connect = ctx.command.name in ('play',)
            if not ctx.author.voice:
                raise self.MusicException('❌ Musisz być połączony do kanału głosowego!')

            if not ctx.guild.voice_client:
                if not should_connect:
                    raise self.MusicException('🙊 Atorin nie jest połączony do kanału głosowego!')

                permissions = ctx.author.voice.channel.permissions_for(ctx.me)

                if not permissions.connect or not permissions.speak:
                    raise self.MusicException('🚫 Atorin nie ma uprawnień potrzebych do odtwarzania muzyki.'
                                              ' Daj roli `Atorin` uprawnienia `Łączenie` oraz `Mówienie`'
                                              ' i spróbuj ponownie.')
            else:
                if int(ctx.guild.voice_client.channel.id) != ctx.author.voice.channel.id:
                    raise self.MusicException('❌ Nie jesteś połączony do kanału na którym jest Atorin!')
        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, self.MusicException):
            await ctx.send(error.original)

    @commands.command(
        description="Odtwarza muzykę na kanale głosowym\n\nPrzykłady użycia:"
                    "\n&play despacito\n&play https://www.youtube.com/watch?v=kJQP7kiw5Fk",
        usage="<tytuł lub link do Youtube>",
        aliases=["p"]
    )
    async def play(self, ctx, *, song):
        voice_channel = ctx.author.voice.channel
        voice = ctx.guild.voice_client
        searching = await ctx.send("🔎 Trwa wyszukiwanie utworu...")
        videos_search = VideosSearch(song, limit=5, region="PL")
        results = await videos_search.next()
        if not results:
            await ctx.send("❌ Nie znaleziono utworów o podanej nazwie.")
            return
        embed = self.bot.embed(ctx.author)
        embed.title = "Wyniki wyszukiwania"
        embed.description = "❓ **Wybierz utwór, którego szukasz.**\n\n"
        i = 0
        for result in results["result"][:5]:
            i = i + 1
            embed.description += "**#{}**. {} ({})\n".format(
                i, (result["title"][:50] + "...") if len(result["title"]) > 53 else result["title"], result["duration"]
            )
        await searching.edit(content=None, embed=embed)
        reactions = {"1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5, "❌": 0}
        for reaction in reactions.keys():
            await searching.add_reaction(reaction)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in reactions

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)
        except TimeoutError:
            await searching.edit(embed=None, content="🔇 Nie wybrano utworu.")
            await searching.clear_reactions()
            return
        if reactions[str(reaction.emoji)] == 0:
            await searching.edit(embed=None, content="🔇 Nie wybrano utworu.")
            await searching.clear_reactions()
            return
        await searching.clear_reactions()
        choice = reactions[str(reaction.emoji)] - 1
        metadata = results["result"][choice]
        await searching.edit(content="✅ Wybrano **#{}**. **{}** ({}).".format(
            choice + 1, metadata["title"], metadata["duration"]
        ), embed=None)
        info_message = await ctx.send("💿 Trwa przygotowywanie utworu...")
        try:
            duration = datetime.strptime(metadata["duration"], "%H:%M:%S")
        except ValueError:
            duration = datetime.strptime(metadata["duration"], "%M:%S")
        if duration.hour > 0 or duration.minute > 10:
            await info_message.edit(content="❌ Podany utwór jest za długi, limit to 10 minut.")
            return
        if not os.path.isfile("../songs/" + metadata["id"] + ".m4a"):
            await info_message.edit(content="💾 Pobieranie utworu...")
            ytdl.download(["https://www.youtube.com/watch?v=" + metadata["id"]])
            await info_message.edit(content="✅ Pobrano.")
        if not voice:
            await info_message.edit(content="🎙️ Dołączanie do kanału...")
            try:
                voice = await voice_channel.connect()
            except discord.ClientException:
                await info_message.edit(content="❌ Atorin jest już podłączony do kanału głosowego!")
                return
            await info_message.edit(content="✅ Dołączono.")
        player = self.get_player(ctx)
        metadata["requester"] = ctx.author
        await player.queue.put(metadata)
        if voice.is_playing():
            await info_message.edit(content="📩 Utwór **{}** został dodany do kolejki.".format(metadata["title"]))
        else:
            await info_message.delete()

    @commands.command(
        description="Wstrzymuje odtwarzanie muzyki",
        aliases=["zatrzymaj"]
    )
    async def pause(self, ctx):
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
    async def resume(self, ctx):
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
    async def stop(self, ctx):
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
    async def skip(self, ctx):
        voice = ctx.guild.voice_client
        if voice and voice.is_playing():
            voice.stop()
            await ctx.send("⏭️Pominięto utwór.")
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Ustawia głośność aktualnie odtwarzanego utworu",
        aliases=["głośność", "glosnosc"],
        usage="<0-100>"
    )
    async def volume(self, ctx, vol: int):
        if vol > 100 or vol < 0:
            raise commands.BadArgument
        voice = ctx.guild.voice_client
        if voice and voice.is_playing():
            player = self.get_player(ctx)
            source = player.source
            source.volume = float(vol / 100)
            await ctx.send("🔉 Ustawiono glośność na {}%.".format(vol))
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Wyświetla kolejkę utworów do odtworzenia",
        aliases=["kolejka"]
    )
    async def queue(self, ctx):
        voice = ctx.guild.voice_client
        if voice and voice.is_playing():
            player = self.get_player(ctx)
            if player.queue.empty():
                return await ctx.send('🕳️ Kolejka jest pusta!')

            upcoming = list(itertools.islice(player.queue._queue, 0, 5))

            fmt = '\n'.join(
                f'**{_["title"]}** ({time.strftime("%H:%M:%S", time.gmtime(_["duration"]))})' for _ in upcoming)
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
    async def nowplaying(self, ctx):
        voice = ctx.guild.voice_client
        if voice and voice.is_playing():
            player = self.get_player(ctx)
            song = player.now_playing
            embed = ctx.bot.embed(ctx.author)
            embed.title = "Teraz odtwarzane"
            embed.add_field(name="🎧 Utwór", value=song["title"], inline=False)
            embed.add_field(name="🛤️ Długość", value=time.strftime("%H:%M:%S", time.gmtime(song["duration"])))
            embed.add_field(name="💃 Zaproponowany przez", value=ctx.author.mention)
            embed.set_thumbnail(url=song["thumbnail"])
            await ctx.send(embed=embed)
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
