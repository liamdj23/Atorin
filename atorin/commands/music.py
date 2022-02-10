import base64
import re

from datetime import timedelta
import lavalink
from discord.ext import commands
from discord.commands import slash_command, Option
import discord
import requests

from atorin.bot import Atorin
from ..utils import progress_bar
from ..config import config
from .. import metrics

url_rx = re.compile(r"https?://(?:www\.)?.+")

address: str = config["lavalink"]["host"] or "127.0.0.1"
port: int = config["lavalink"]["port"] or 2333
password: str = config["lavalink"]["password"] or "youshallnotpass"
region: str = config["lavalink"]["region"] or "eu"
node: str = config["lavalink"]["node"] or "default-node"


class LavalinkVoiceClient(discord.VoiceClient):
    """
    This is the preferred way to handle external voice sending
    This client will be created via a cls in the connect method of the channel
    see the following documentation:
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """

    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {"t": "VOICE_SERVER_UPDATE", "d": data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {"t": "VOICE_STATE_UPDATE", "d": data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel)
        metrics.active_players.inc()

    async def disconnect(self, *, force: bool) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that
        # would set channel_id to None doesn't get dispatched after the
        # disconnect
        player.channel_id = None
        self.cleanup()
        metrics.active_players.dec()


def get_song_from_spotify(id: str) -> str:
    authorization_token = base64.b64encode(
        f"{config['spotify']['client_id']}:{config['spotify']['client_secret']}".encode()
    ).decode("utf-8")
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {authorization_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Atorin",
        },
        params={"grant_type": "client_credentials"},
    )
    if r.status_code == 200:
        token = r.json()["access_token"]
        r = requests.get(
            f"https://api.spotify.com/v1/tracks/{id}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Atorin",
            },
        )
        if r.status_code == 200:
            song = r.json()
            return f"{song['artists'][0]['name']} {song['name']}"
        else:
            raise commands.CommandError("Nie znaleziono podanego utworu!")
    else:
        raise commands.CommandError(
            "Nie udało się uzyskać tokenu z API Spotify, spróbuj ponownie później."
        )


class Music(commands.Cog, name="🎵 Muzyka (beta)"):
    def __init__(self, bot: Atorin):
        self.bot = bot

        if self.bot and not hasattr(self.bot, "lavalink"):
            lavalink.add_event_hook(self.track_hook)
            self.bot.lavalink = lavalink.Client(config["dashboard"]["client_id"])
            self.bot.lavalink.add_node(address, port, password, region, node)
            self.bot.add_listener(
                self.bot.lavalink.voice_update_handler, "on_socket_response"
            )

    def cog_unload(self):
        """Cog unload handler. This removes any event hooks that were registered."""
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """Command before-invoke handler."""
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def ensure_voice(self, ctx):
        """This check ensures that the bot and command author are in the same voicechannel."""
        player = self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region)
        )
        # Create returns a player if one exists, otherwise creates.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        if isinstance(ctx.command, str):
            should_connect = ctx.command in ("play",)
        else:
            should_connect = ctx.command.name in ("play",)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError(
                "Musisz być połączony do kanału głosowego!"
            )

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError("Atorin nie odtwarza muzyki!")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError(
                    "Atorin nie ma uprawnień potrzebnych do odtwarzania muzyki."
                    " Daj roli `Atorin` uprawnienia `Łączenie` oraz `Mówienie`"
                    " i spróbuj ponownie."
                )

            player.store("channel", ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError(
                    "Nie jesteś połączony do kanału na którym jest Atorin!"
                )

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            guild: discord.Guild = self.bot.get_guild(guild_id)
            player = self.bot.lavalink.player_manager.get(guild_id)
            if not player.is_connected:
                return
            player.queue.clear()
            await player.stop()
            await guild.voice_client.disconnect(force=True)
        if isinstance(event, lavalink.events.TrackStartEvent):
            song = event.track
            channel = self.bot.get_channel(event.player.fetch("channel"))
            embed = discord.Embed()
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
            metrics.songs.labels(song=song.title).inc()

    @slash_command(
        description="Odtwarza utwór lub playlistę z YT/Twitch/MP3 na kanale głosowym",
        guild_ids=config["guild_ids"],
    )
    async def play(
        self,
        ctx: discord.ApplicationContext,
        query: Option(str, "Tytuł lub link do Youtube/Twitch/MP3"),
    ):
        """Searches and plays a song from a given query."""
        await ctx.defer()
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip("<>")

        if not url_rx.match(query):
            query = f"ytsearch:{query}"
        else:
            if "open.spotify.com/track/" in query:
                song = get_song_from_spotify(
                    query.split("open.spotify.com/track/")[1].split("?")[0]
                )
                query = f"ytsearch:{song}"
            elif "spotify:track:" in query:
                song = get_song_from_spotify(query.split("spotify:track:")[1])
                query = f"ytsearch:{song}"

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send_followup("❌ Nie znaleziono utworu o podanej nazwie!")

        embed = discord.Embed()

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

        await ctx.send_followup(embed=embed)

        if not player.is_playing:
            await player.play()

    @slash_command(
        description="Rozłącza bota z kanału głosowego", guild_ids=config["guild_ids"]
    )
    async def stop(self, ctx: discord.ApplicationContext):
        """Disconnects the player from the voice channel and clears its queue."""
        await ctx.defer()
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.is_playing:
            player.queue.clear()
            await player.stop()
            await ctx.voice_client.disconnect(force=True)
            await ctx.send_followup("⏹ Zatrzymano odtwarzanie.")
        else:
            await ctx.send_followup("🙊 Atorin nie odtwarza muzyki.")

    @slash_command(
        description="Wstrzymuje odtwarzanie muzyki", guild_ids=config["guild_ids"]
    )
    async def pause(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.paused:
            await player.set_pause(True)
            await ctx.send_followup(
                "⏸ Wstrzymano odtwarzanie. Aby wznowić wpisz `/resume`."
            )
        else:
            await ctx.send_followup("🙊 Atorin nie odtwarza muzyki.")

    @slash_command(
        description="Wznawia odtwarzanie muzyki", guild_ids=config["guild_ids"]
    )
    async def resume(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.paused:
            await player.set_pause(False)
            await ctx.send_followup("▶️ Wznowiono odtwarzanie.")
        else:
            await ctx.send_followup("🙊 Atorin nie odtwarza muzyki.")

    @slash_command(
        description="Pomija aktualnie odtwarzany utwór", guild_ids=config["guild_ids"]
    )
    async def skip(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.is_playing:
            await player.skip()
            await ctx.send_followup("⏭ ️Pominięto utwór.")
        else:
            await ctx.send_followup("🙊 Atorin nie odtwarza muzyki.")

    @slash_command(
        description="Ustawia głośność aktualnie odtwarzanego utworu",
        guild_ids=config["guild_ids"],
    )
    async def volume(
        self, ctx: discord.ApplicationContext, vol: Option(int, "Głośność od 1 do 100")
    ):
        await ctx.defer()
        if vol > 100 or vol < 0:
            raise commands.BadArgument("Wartość musi być w przedziale od 1 do 100!")
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.is_playing:
            await player.set_volume(vol)
            await ctx.send_followup("🔉 Ustawiono glośność na {}%.".format(vol))
        else:
            await ctx.send_followup("🙊 Atorin nie odtwarza muzyki.")

    @slash_command(
        description="Wyświetla kolejkę utworów do odtworzenia",
        guild_ids=config["guild_ids"],
    )
    async def queue(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send_followup("🕳️ Kolejka jest pusta!")

        fmt = "\n".join(f"**{song.title}**" for song in player.queue)

        embed = discord.Embed()
        embed.title = f"Utwory w kolejce: {len(player.queue)}"
        embed.description = fmt
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Wyświetla aktualnie odtwarzany utwór",
        guild_ids=config["guild_ids"],
    )
    async def nowplaying(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.is_playing:
            song = player.current
            embed = discord.Embed()
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
            await ctx.send_followup(embed=embed)
        else:
            await ctx.send_followup("🙊 Atorin nie odtwarza muzyki.")

    @slash_command(
        description="Ustawia powtarzanie aktualnie odtwarzanego utworu",
        guild_ids=config["guild_ids"],
    )
    async def loop(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.repeat:
            player.repeat = False
        else:
            player.repeat = True
        await ctx.send_followup(
            f"🔂 Powtarzanie aktualnego utworu zostało {'włączone' if player.repeat else 'wyłączone'}."
        )

    @slash_command(
        description="Ustawia losowe odtwarzanie kolejki", guild_ids=config["guild_ids"]
    )
    async def shuffle(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.shuffle:
            player.shuffle = False
        else:
            player.shuffle = True
        await ctx.send_followup(
            f"🔀 Losowe odtwarzanie kolejki zostało {'włączone' if player.shuffle else 'wyłączone'}."
        )

    @slash_command(description="Bass Boost", guild_ids=config["guild_ids"])
    async def bassboost(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(
            ctx.guild.id
        )
        if not player.fetch("bassboost"):
            await player.set_gains((0, 0.50), (1, 0.50), (2, 0.50))
            player.store("bassboost", True)
        else:
            await player.reset_equalizer()
            player.store("bassboost", False)
        await ctx.send_followup(
            f"🎚 Bass boost został **{'włączony' if player.fetch('bassboost') else 'wyłączony'}**."
        )


def setup(bot):
    bot.add_cog(Music(bot))
