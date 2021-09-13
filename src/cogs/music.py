import re

from datetime import timedelta
import lavalink
from discord.ext import commands

from utils import progress_bar

url_rx = re.compile(r"https?://(?:www\.)?.+")


class Music(commands.Cog, name="🎵 Muzyka (beta)"):
    def __init__(self, bot):
        self.bot = bot

        address = self.bot.config["lavalink_address"] or "127.0.0.1"
        port = self.bot.config["lavalink_port"] or 2333
        password = self.bot.config["lavalink_password"] or "youshallnotpass"
        region = self.bot.config["lavalink_region"] or "eu"
        node = self.bot.config["lavalink_node"] or "default-node"
        if not hasattr(
            bot, "lavalink"
        ):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node(address, port, password, region, node)
            bot.add_listener(bot.lavalink.voice_update_handler, "on_socket_response")

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        """Cog unload handler. This removes any event hooks that were registered."""
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """Command before-invoke handler."""
        guild_check = ctx.guild is not None

        if guild_check:
            await self.ensure_voice(ctx)

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

    async def ensure_voice(self, ctx):
        """This check ensures that the bot and command author are in the same voicechannel."""
        player = self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region)
        )
        # Create returns a player if one exists, otherwise creates.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        should_connect = ctx.command.name in ("play",)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError(
                "❌ Musisz być połączony do kanału głosowego!"
            )

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError(
                    "❌ Atorin nie jest połączony do kanału głosowego!"
                )

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError(
                    "❌ Atorin nie ma uprawnień potrzebych do odtwarzania muzyki."
                    " Daj roli `Atorin` uprawnienia `Łączenie` oraz `Mówienie`"
                    " i spróbuj ponownie."
                )

            player.store("channel", ctx.channel.id)
            await ctx.guild.change_voice_state(channel=ctx.author.voice.channel)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError(
                    "❌ Nie jesteś połączony do kanału na którym jest Atorin!"
                )

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)
            await guild.change_voice_state(channel=None)
        if isinstance(event, lavalink.events.TrackStartEvent):
            song = event.track
            channel = self.bot.get_channel(event.player.fetch("channel"))
            embed = self.bot.embed()
            embed.title = "Teraz odtwarzane"
            embed.add_field(name="🎧 Utwór", value=song.title, inline=False)
            if not song.duration == 9223372036854775807:
                embed.add_field(
                    name="🛤️ Długość",
                    value=str(timedelta(milliseconds=song.duration)).split(".")[0],
                )
            else:
                embed.add_field(name="🛤️ Długość", value="🔴 Na żywo")
            embed.add_field(name="💃 Zaproponowany przez", value=f"<@{song.requester}>")
            embed.set_thumbnail(
                url=f"https://img.youtube.com/vi/{song.identifier}/maxresdefault.jpg"
            )
            await channel.send(embed=embed)

    @commands.command(
        description="Odtwarza utwór lub playlistę z YT/Twitch/MP3 na kanale głosowym\n\nPrzykłady użycia:"
        "\n&play despacito\n&play https://www.youtube.com/watch?v=kJQP7kiw5Fk",
        usage="<tytuł lub link do Youtube/Twitch/MP3>",
        aliases=["p"],
    )
    async def play(self, ctx, *, query: str):
        """Searches and plays a song from a given query."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip("<>")

        if not url_rx.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send("❌ Nie znaleziono utworu o podanej nazwie!")

        embed = ctx.bot.embed(ctx.author)

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = "Dodano playlistę do kolejki!"
            embed.description = (
                f'{results["playlistInfo"]["name"]} - {len(tracks)} utworów'
            )
        else:
            track = results["tracks"][0]
            embed.title = "Dodano do kolejki"
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            embed.set_thumbnail(
                url=f"https://img.youtube.com/vi/{track['info']['identifier']}/maxresdefault.jpg"
            )
            track = lavalink.models.AudioTrack(track, ctx.author.id)
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)

        if not player.is_playing:
            await player.play()

    @commands.command(aliases=["dc", "leave"])
    async def disconnect(self, ctx):
        """Disconnects the player from the voice channel and clears its queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send("❌ Atorin nie jest połączony do kanału głosowego!")

        if not ctx.author.voice or (
            player.is_connected
            and ctx.author.voice.channel.id != int(player.channel_id)
        ):
            return await ctx.send(
                "❌ Nie jesteś połączony do kanału na którym jest Atorin!"
            )

        player.queue.clear()
        await player.stop()
        await ctx.guild.change_voice_state(channel=None)
        await ctx.send("🔇 Rozłączono.")

    @commands.command(
        description="Wstrzymuje odtwarzanie muzyki", aliases=["zatrzymaj"]
    )
    async def pause(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.paused:
            await player.set_pause(True)
            await ctx.send("⏸ Wstrzymano odtwarzanie. Aby wznowić wpisz `&resume`.")
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Wznawia odtwarzanie muzyki", aliases=["wznów", "wznow"]
    )
    async def resume(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.paused:
            await player.set_pause(False)
            await ctx.send("▶️ Wznowiono odtwarzanie.")
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(description="Zatrzymuje odtwarzanie muzyki")
    async def stop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.is_playing:
            player.queue.clear()
            await player.stop()
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Pomija aktualnie odtwarzany utwór", aliases=["pomiń", "pomin", "s"]
    )
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.is_playing:
            await player.skip()
            await ctx.send("⏭ ️Pominięto utwór.")
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Ustawia głośność aktualnie odtwarzanego utworu",
        aliases=["głośność", "glosnosc", "vol"],
        usage="<0-100>",
    )
    async def volume(self, ctx, vol: int):
        if vol > 100 or vol < 0:
            raise commands.BadArgument
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.is_playing:
            await player.set_volume(vol)
            await ctx.send("🔉 Ustawiono glośność na {}%.".format(vol))
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")
        return

    @commands.command(
        description="Wyświetla kolejkę utworów do odtworzenia", aliases=["kolejka"]
    )
    async def queue(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send("🕳️ Kolejka jest pusta!")

        fmt = "\n".join(f"**{song.title}**" for song in player.queue)

        embed = self.bot.embed(ctx.author)
        embed.title = f"Utwory w kolejce: {len(player.queue)}"
        embed.description = fmt
        await ctx.send(embed=embed)

    @commands.command(
        description="Wyświetla aktualnie odtwarzany utwór", aliases=["np", "nowp"]
    )
    async def nowplaying(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.is_playing:
            song = player.current
            embed = ctx.bot.embed(ctx.author)
            embed.title = "Teraz odtwarzane"
            embed.add_field(name="🎧 Utwór", value=song.title, inline=False)
            if not song.duration == 9223372036854775807:
                duration = str(timedelta(milliseconds=song.duration))
                position = str(timedelta(milliseconds=round(player.position))).split(
                    "."
                )[0]
                progress = progress_bar(round(player.position) / song.duration * 100)[
                    :-5
                ]
                embed.add_field(
                    name="🛤️ Postęp",
                    value=f"```css\n{progress} {position}/{duration}```",
                    inline=False,
                )
            else:
                embed.add_field(name="🛤️ Postęp", value="🔴 Na żywo")
            embed.add_field(name="💃 Zaproponowany przez", value=f"<@{song.requester}>")
            embed.set_thumbnail(
                url=f"https://img.youtube.com/vi/{song.identifier}/maxresdefault.jpg"
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("🙊 Atorin nie odtwarza muzyki.")

    @commands.command(
        description="Ustawia powtarzanie aktualnie odtwarzanego utworu",
        aliases=["repeat", "powtarzaj"],
    )
    async def loop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.repeat:
            player.repeat = False
        else:
            player.repeat = True
        await ctx.send(
            f"🔂 Powtarzanie aktualnego utworu zostało {'włączone' if player.repeat else 'wyłączone'}."
        )


def setup(bot):
    bot.add_cog(Music(bot))
