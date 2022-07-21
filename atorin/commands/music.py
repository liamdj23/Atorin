import base64
import re

from datetime import timedelta
from bs4 import BeautifulSoup, Tag
import lavalink
from discord.ext import commands
from discord.commands import slash_command, Option, SlashCommandGroup
import discord
import httpx

from atorin.bot import Atorin
from ..utils import progress_bar
from ..config import config

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


async def get_song_from_spotify(id: str) -> str:
    authorization_token = base64.b64encode(
        f"{config['spotify']['client_id']}:{config['spotify']['client_secret']}".encode()
    ).decode("utf-8")
    async with httpx.AsyncClient() as client:
        r = await client.post(
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
        async with httpx.AsyncClient() as client:
            r = await client.get(
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
        elif r.status_code == 400:
            raise commands.BadArgument("Song not found!")
        else:
            raise commands.CommandError(
                f"Error has occurred while downloading informations from Spotify, try again later. [{r.status_code}]"
            )
    else:
        raise commands.CommandError(f"Unable to fetch token from Spotify API, try again later. [{r.status_code}]")


class Music(commands.Cog, name="🎵 Muzyka"):
    def __init__(self, bot: Atorin):
        self.bot = bot

        if self.bot and not hasattr(self.bot, "lavalink"):
            lavalink.add_event_hook(self.track_hook)
            self.bot.lavalink = lavalink.Client(config["dashboard"]["client_id"])
            self.bot.lavalink.add_node(address, port, password, region, node)
            self.bot.add_listener(self.bot.lavalink.voice_update_handler, "on_socket_response")

    def cog_unload(self):
        """Cog unload handler. This removes any event hooks that were registered."""
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx: discord.ApplicationContext):
        """Command before-invoke handler."""
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def ensure_voice(self, ctx: discord.ApplicationContext):
        # These are commands that doesn't require author to join a voicechannel
        if ctx.command.name in ("lyrics",):
            return True

        """This check ensures that the bot and command author are in the same voicechannel."""
        player = self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.author.voice.channel.rtc_region)
        )
        # Create returns a player if one exists, otherwise creates.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        if isinstance(ctx.command, str):
            should_connect = ctx.command in ("play",)
        else:
            should_connect = ctx.command.name in ("play",)

        embed = discord.Embed()
        embed.color = 0xFF0000
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed.description = (
                "❌ Musisz być połączony do kanału głosowego!"
                if ctx.interaction.locale == "pl"
                else "❌ You must be connected to a voice channel!"
            )
            await ctx.respond(embed=embed)
            return

        if not player.is_connected:
            if not should_connect:
                embed.description = (
                    "❌ Atorin nie odtwarza muzyki!"
                    if ctx.interaction.locale == "pl"
                    else "❌ Atorin is not playing music!"
                )
                await ctx.respond(embed=embed)
                return

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                embed.description = (
                    "❌ Atorin nie ma uprawnień potrzebnych do odtwarzania muzyki. Daj roli `Atorin` uprawnienia `Łączenie` oraz `Mówienie` i spróbuj ponownie."
                    if ctx.interaction.locale == "pl"
                    else "❌ Atorin doesn't have permissions for playing music. Add `Connect` and `Speak` permissions to `Atorin` role and try again."
                )
                await ctx.respond(embed=embed)
                return

            player.store("channel", ctx.channel.id)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                embed.description = (
                    "❌ Nie jesteś połączony do kanału na którym jest Atorin!"
                    if ctx.interaction.locale == "pl"
                    else "❌ You are not connected to a voice channel where Atorin is playing music!"
                )
                await ctx.respond(embed=embed)
                return

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

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ):
        vc: discord.VoiceChannel = before.channel
        if vc:
            player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(vc.guild.id)
            if player:
                if player.channel_id == vc.id and vc.members == [vc.guild.me]:
                    await player.stop()
                    await vc.guild.change_voice_state(channel=None)

    @slash_command(
        description="Play music from YT/Spotify/Twitch/MP3",
        description_localizations={"pl": "Odtwarza utwór lub playlistę z YT/Spotify/Twitch/MP3 na kanale głosowym"},
        guild_ids=config["guild_ids"],
    )
    async def play(
        self,
        ctx: discord.ApplicationContext,
        query: Option(
            str,
            name="song",
            name_localizations={"pl": "piosenka"},
            description="Title or url to YT/Spotify/Twitch/MP3",
            description_localizations={"pl": "Tytuł lub link do Youtube/Spotify/Twitch/MP3"},
        ),
    ):
        """Searches and plays a song from a given query."""
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        player.store("lang", ctx.interaction.guild_locale)
        query = query.strip("<>")

        if not url_rx.match(query):
            query = f"ytsearch:{query}"
        else:
            if "open.spotify.com/track/" in query:
                song = await get_song_from_spotify(query.split("open.spotify.com/track/")[1].split("?")[0])
                query = f"ytsearch:{song}"
            elif "spotify:track:" in query:
                song = await get_song_from_spotify(query.split("spotify:track:")[1])
                query = f"ytsearch:{song}"

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            raise commands.BadArgument(
                "Nie znaleziono utworu o podanej nazwie!" if ctx.interaction.locale == "pl" else "Song not found!"
            )

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

            embed.title = (
                "Dodano playlistę do kolejki!" if ctx.interaction.locale == "pl" else "Playlist added to queue!"
            )
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} {"utworów" if ctx.interaction.locale == "pl" else "tracks"}'
        else:
            track = results["tracks"][0]
            embed.title = "Dodano do kolejki" if ctx.interaction.locale == "pl" else "Added to queue"
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track['info']['identifier']}/maxresdefault.jpg")
            track = lavalink.models.AudioTrack(track, ctx.author.id)
            player.add(requester=ctx.author.id, track=track)

        await ctx.send_followup(embed=embed)

        if not player.is_playing:
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
            await player.play()

    @slash_command(
        description="Disconnects Atorin from voice channel",
        description_localizations={"pl": "Rozłącza bota z kanału głosowego"},
        guild_ids=config["guild_ids"],
    )
    async def stop(self, ctx: discord.ApplicationContext):
        """Disconnects the player from the voice channel and clears its queue."""
        await ctx.defer()
        embed = discord.Embed()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.is_playing:
            player.queue.clear()
            await player.stop()
            await ctx.voice_client.disconnect(force=True)
            embed.description = "⏹ **Zatrzymano odtwarzanie.**" if ctx.interaction.locale == "pl" else "⏹ **Stopped.**"
            await ctx.send_followup(embed=embed)
        else:
            embed.color = 0xFF0000
            embed.description = (
                "❌ Atorin nie odtwarza muzyki!" if ctx.interaction.locale == "pl" else "❌ Atorin is not playing music!"
            )
            await ctx.send_followup(embed=embed)

    @slash_command(
        description="Pause music",
        description_localizations={"pl": "Wstrzymuje odtwarzanie muzyki"},
        guild_ids=config["guild_ids"],
    )
    async def pause(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        embed = discord.Embed()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.paused:
            await player.set_pause(True)
            embed.description = (
                "⏸ **Wstrzymano odtwarzanie. Aby wznowić wpisz `/resume`.**"
                if ctx.interaction.locale == "pl"
                else "⏸ **Paused. To resume playing, use `/resume`.**"
            )
            await ctx.send_followup(embed=embed)
        else:
            embed.color = 0xFF0000
            embed.description = (
                "❌ Atorin nie odtwarza muzyki!" if ctx.interaction.locale == "pl" else "❌ Atorin is not playing music!"
            )
            await ctx.send_followup(embed=embed)

    @slash_command(
        description="Resume music",
        description_localizations={"pl": "Wznawia odtwarzanie muzyki"},
        guild_ids=config["guild_ids"],
    )
    async def resume(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed()
        if player.paused:
            await player.set_pause(False)
            embed.description = "▶️ **Wznowiono odtwarzanie.**" if ctx.interaction.locale == "pl" else "▶️ **Resumed**"
            await ctx.send_followup(embed=embed)
        else:
            embed.color = 0xFF0000
            embed.description = (
                "❌ Atorin nie odtwarza muzyki!" if ctx.interaction.locale == "pl" else "❌ Atorin is not playing music!"
            )
            await ctx.send_followup(embed=embed)

    @slash_command(
        description="Skip song",
        description_localizations={"pl": "Pomija aktualnie odtwarzany utwór"},
        guild_ids=config["guild_ids"],
    )
    async def skip(
        self,
        ctx: discord.ApplicationContext,
        number: Option(
            int,
            name="number",
            name_localizations={"pl": "numer"},
            description="Type numer of song you want to play",
            description_localizations={"pl": "Podaj numer utworu który chcesz odtworzyć"},
            min_value=1,
        ) = None,
    ):
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed()
        if player.is_playing:
            if number:
                if number > len(player.queue):
                    raise commands.BadArgument(
                        "Podano niepoprawny numer utworu! Sprawdź kolejkę komendą `/queue view`"
                        if ctx.interaction.locale == "pl"
                        else "Track number is not valid! Check queue by using `/queue view`"
                    )
                player.queue = player.queue[number - 1 :]
            await player.skip()
            embed.description = "⏭ ️**Pominięto utwór.**" if ctx.interaction.locale == "pl" else "⏭ ️**Skipped.**"
            await ctx.send_followup(embed=embed)
        else:
            embed.color = 0xFF0000
            embed.description = (
                "❌ Atorin nie odtwarza muzyki!" if ctx.interaction.locale == "pl" else "❌ Atorin is not playing music!"
            )
            await ctx.send_followup(embed=embed)

    @slash_command(
        description="Set volume",
        description_localizations={"pl": "Ustawia głośność aktualnie odtwarzanego utworu"},
        guild_ids=config["guild_ids"],
    )
    async def volume(
        self,
        ctx: discord.ApplicationContext,
        vol: Option(
            int,
            name="volume",
            name_localizations={"pl": "głośność"},
            description="Volume from 1 to 100",
            description_localizations={"pl": "Głośność od 1 do 100"},
            min_value=1,
            max_value=100,
        ),
    ):
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed()
        if player.is_playing:
            await player.set_volume(vol)
            embed.description = (
                f"🔉 **Ustawiono glośność na {vol}%.**"
                if ctx.interaction.locale == "pl"
                else f"🔉 **Volume set to {vol}%.**"
            )
            await ctx.send_followup(embed=embed)
        else:
            embed.color = 0xFF0000
            embed.description = (
                "❌ Atorin nie odtwarza muzyki!" if ctx.interaction.locale == "pl" else "❌ Atorin is not playing music!"
            )
            await ctx.send_followup(embed=embed)

    queue_group = SlashCommandGroup(
        name="queue",
        description="Queue management commands",
        description_localizations={"pl": "Komendy do zarządzania kolejką odtwarzania"},
        guild_ids=config["guild_ids"],
    )

    @queue_group.command(
        name="view",
        description="Show queue",
        description_localizations={"pl": "Wyświetla kolejkę utworów do odtworzenia"},
    )
    async def queue_view(self, ctx: discord.ApplicationContext):
        emoji_numbers = {
            1: "1️⃣",
            2: "2️⃣",
            3: "3️⃣",
            4: "4️⃣",
            5: "5️⃣",
            6: "6️⃣",
            7: "7️⃣",
            8: "8️⃣",
            9: "9️⃣",
            10: "🔟",
        }
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed()
        if not player.queue:
            embed.description = (
                "🕳️ **Kolejka jest pusta!**" if ctx.interaction.locale == "pl" else "🕳️ **Queue is empty!**"
            )
            return await ctx.send_followup(embed=embed)
        fmt = "\n".join(f"{emoji_numbers[i]} **{song.title}**" for i, song in enumerate(player.queue, start=1))
        embed.title = (
            f"{'Utwory w kolejce' if ctx.interaction.locale == 'pl' else 'Tracks in queue'}: {len(player.queue)}"
        )
        embed.description = fmt
        await ctx.send_followup(embed=embed)

    @queue_group.command(
        name="clear",
        description="Clear queue",
        description_localizations={"pl": "Czyści kolejkę"},
    )
    async def queue_clear(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed()
        if not player.queue:
            embed.description = (
                "🕳️ **Kolejka jest pusta!**" if ctx.interaction.locale == "pl" else "🕳️ **Queue is empty!**"
            )
            return await ctx.send_followup(embed=embed)
        embed.title = "Wyczyszczono kolejkę" if ctx.interaction.locale == "pl" else "Queue cleared"
        embed.description = (
            f"✅  **Pomyślnie usunięto *{len(player.queue)}* utworów z kolejki.**"
            if ctx.interaction.locale == "pl"
            else f"✅  **Removed *{len(player.queue)}* tracks from queue.**"
        )
        player.queue = []
        await ctx.send_followup(embed=embed)

    @queue_group.command(
        name="remove",
        description="Remove selected song from queue",
        description_localizations={"pl": "Usuwa z kolejki podany utwór"},
    )
    async def queue_remove(
        self,
        ctx: discord.ApplicationContext,
        number: Option(
            int,
            name="number",
            name_localizations={"pl": "numer"},
            description="Type song number in queue",
            description_localizations={"pl": "Wpisz numer utworu w kolejce"},
            min_value=1,
        ),
    ):
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed()
        if not player.queue:
            embed.description = (
                "🕳️ **Kolejka jest pusta!**" if ctx.interaction.locale == "pl" else "🕳️ **Queue is empty!**"
            )
            return await ctx.send_followup(embed=embed)
        try:
            song: lavalink.AudioTrack = player.queue.pop(number - 1)
        except IndexError:
            raise commands.BadArgument(
                "Podano niepoprawny numer utworu! Sprawdź kolejkę komendą `/queue view`"
                if ctx.interaction.locale == "pl"
                else "Track number is not valid! Check queue by using `/queue view`"
            )
        embed.title = "Usunięto z kolejki" if ctx.interaction.locale == "pl" else "Removed from queue"
        embed.description = f"🗑 {song.title}"
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Show currently playing song",
        description_localizations={"pl": "Wyświetla aktualnie odtwarzany utwór"},
        guild_ids=config["guild_ids"],
    )
    async def nowplaying(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed()
        if player.is_playing:
            song: lavalink.AudioTrack = player.current
            embed.title = "Teraz odtwarzane" if ctx.interaction.locale == "pl" else "Now playing"
            embed.add_field(
                name="🎧 Utwór" if ctx.interaction.locale == "pl" else "🎧 Track", value=song.title, inline=False
            )
            if not song.duration == 9223372036854775807:
                duration = str(timedelta(milliseconds=song.duration))
                position = str(timedelta(milliseconds=round(player.position))).split(".")[0]
                progress = progress_bar(round(player.position) / song.duration * 100)[:-5]
                embed.add_field(
                    name="🛤️ Postęp" if ctx.interaction.locale == "pl" else "🛤️ Progress",
                    value=f"```css\n{progress} {position}/{duration}```",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="🛤️ Postęp" if ctx.interaction.locale == "pl" else "🛤️ Progress",
                    value="🔴 Na żywo" if ctx.interaction.locale == "pl" else "🔴 Live",
                )
            if ctx.interaction.locale == "pl":
                embed.add_field(
                    name="🔂 Powtarzanie utworu",
                    value="✅ Włączone" if player.repeat else "❌ Wyłączone",
                )
                embed.add_field(
                    name="🎚 Bass Boost",
                    value="✅ Włączony" if player.fetch("bassboost") else "❌ Wyłączony",
                )
                embed.add_field(name="🔀 Losowo", value="✅ Włączony" if player.shuffle else "❌ Wyłączony")
            else:
                embed.add_field(
                    name="🔂 Repeat",
                    value="✅ ON" if player.repeat else "❌ OFF",
                )
                embed.add_field(
                    name="🎚 Bass Boost",
                    value="✅ ON" if player.fetch("bassboost") else "❌ OFF",
                )
                embed.add_field(name="🔀 Shuffle", value="✅ ON" if player.shuffle else "❌ OFF")
            embed.add_field(
                name="🔉 Głośność" if ctx.interaction.locale == "pl" else "🔉 Volume", value=f"{player.volume}%"
            )
            embed.add_field(
                name="💃 Zaproponowany przez" if ctx.interaction.locale == "pl" else "💃 Requested by",
                value=f"<@{song.requester}>",
            )
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{song.identifier}/maxresdefault.jpg")
            await ctx.send_followup(embed=embed)
        else:
            embed.color = 0xFF0000
            embed.description = (
                "❌ Atorin nie odtwarza muzyki!" if ctx.interaction.locale == "pl" else "❌ Atorin is not playing music!"
            )
            await ctx.send_followup(embed=embed)

    @slash_command(
        description="Set song repeat",
        description_localizations={"pl": "Ustawia powtarzanie aktualnie odtwarzanego utworu"},
        guild_ids=config["guild_ids"],
    )
    async def loop(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.repeat:
            player.repeat = False
        else:
            player.repeat = True
        if ctx.interaction.locale == "pl":
            await ctx.send_followup(
                f"🔂 Powtarzanie aktualnego utworu zostało {'włączone' if player.repeat else 'wyłączone'}."
            )
        else:
            await ctx.send_followup(f"🔂 Song repeat is now {'enabled' if player.repeat else 'disabled'}.")

    @slash_command(
        description="Play queue randomly",
        description_localizations={"pl": "Ustawia losowe odtwarzanie kolejki"},
        guild_ids=config["guild_ids"],
    )
    async def shuffle(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.shuffle:
            player.shuffle = False
        else:
            player.shuffle = True
        if ctx.interaction.locale == "pl":
            await ctx.send_followup(
                f"🔀 Losowe odtwarzanie kolejki zostało {'włączone' if player.shuffle else 'wyłączone'}."
            )
        else:
            await ctx.send_followup(f"🔀 Shuffle is now {'enabled' if player.shuffle else 'disabled'}.")

    @slash_command(description="Bass Boost", guild_ids=config["guild_ids"])
    async def bassboost(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        equalizer = lavalink.filters.Equalizer()
        if not player.fetch("bassboost"):
            bands = [(0, 0.25), (1, 0.25), (2, 0.25)]
            equalizer.update(bands=bands)
            await player.set_filter(equalizer)
            player.store("bassboost", True)
        else:
            await player.remove_filter(equalizer)
            player.store("bassboost", False)
        if ctx.interaction.locale == "pl":
            await ctx.send_followup(
                f"🎚 Bass boost został **{'włączony' if player.fetch('bassboost') else 'wyłączony'}**."
            )
        else:
            await ctx.send_followup(
                f"🎚 Bass boost is now **{'enabled' if player.fetch('bassboost') else 'disabled'}**."
            )

    @slash_command(
        description="Lyrics", description_localizations={"pl": "Tekst piosenki"}, guild_ids=config["guild_ids"]
    )
    async def lyrics(
        self,
        ctx: discord.ApplicationContext,
        title: Option(
            str,
            name="title",
            name_localizations={"pl": "tytuł"},
            description="Song title, leave blank if you want lyrics of currently playing song",
            description_localizations={
                "pl": "Podaj tytuł utworu lub pozostaw puste, jeśli chcesz tekst aktualnie odtwarzanego utworu"
            },
        ) = None,
    ):
        await ctx.defer()
        from_player: bool = False
        if not title:
            player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
            if not player or not player.is_playing:
                raise commands.BadArgument(
                    "Atorin nie odtwarza muzyki, musisz podać tytuł utworu!"
                    if ctx.interaction.locale == "pl"
                    else "Atorin is not playing music, you have to enter song title!"
                )
            song: lavalink.AudioTrack = player.current
            title: str = song.title.split(" (")[0]
            from_player = True
        async with httpx.AsyncClient() as client:
            search = await client.get(
                "https://genius.com/api/search/multi",
                params={"q": title},
                headers={"User-agent": "Atorin"},
            )
        if not search.status_code == 200:
            raise commands.CommandError(
                f"Wystąpił błąd podczas wyszukiwania tekstu piosenki! [{search.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while searching for lyrics! [{search.status_code}]"
            )
        search_data = search.json()["response"]["sections"]
        if not search_data:
            if from_player:
                raise commands.BadArgument(
                    "Nie znaleziono tekstu odtwarzanego utworu! Spróbuj wpisać komendę jeszcze raz, podając tytuł utworu."
                    if ctx.interaction.locale == "pl"
                    else "Lyrics of currently playing song cannot be found! Try enter the song title when using this command."
                )
            else:
                raise commands.BadArgument(
                    "Nie znaleziono tekstu podanego utworu!" if ctx.interaction.locale == "pl" else "Lyrics not found!"
                )
        for section in search_data:
            if section["type"] == "song":
                lyrics_data = section["hits"][0]["result"]
        lyrics_url = lyrics_data["path"]
        lyrics_artist = lyrics_data["artist_names"]
        lyrics_title = lyrics_data["title"]
        lyrics_thumbnail = lyrics_data["song_art_image_url"]
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://genius.com{lyrics_url}", headers={"User-agent": "Atorin"})
        if not r.status_code == 200:
            raise commands.CommandError(
                f"Wystąpił błąd podczas pobierania tekstu piosenki! [{r.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while downloading lyrics! [{r.status_code}]"
            )
        soup = BeautifulSoup(r.content, "html.parser")
        containers: list[Tag] = soup.find_all("div", attrs={"data-lyrics-container": "true"})
        if not containers:
            raise commands.CommandError(
                f"Wystąpił błąd podczas przetwarzania tekstu! [No lyrics container]"
                if ctx.interaction.locale == "pl"
                else "Error has occurred while processing lyrics! [No lyrics container]"
            )
        lyrics: str = ""
        for container in containers:
            i_tags: list[Tag] = container.find_all("i")
            for tag in i_tags:
                tag.replace_with(f"*{tag.text}*")
            b_tags: list[Tag] = container.find_all("b")
            for tag in b_tags:
                tag.replace_with(f"**{tag.text}**")
            lyrics += container.get_text("\n", strip=True) + "\n"
        splited_lyrics = lyrics.splitlines()
        for i, line in enumerate(splited_lyrics):
            if line.startswith("[") and line.endswith("]"):
                splited_lyrics[i] = f"\n**{line}**"
        lyrics = "\n".join(splited_lyrics)
        embed = discord.Embed()
        embed.title = f"🎶 {lyrics_artist} - {lyrics_title}"
        embed.set_thumbnail(url=lyrics_thumbnail)
        if len(lyrics) > 4096:
            splited_message = []
            limit = 4096
            for i in range(0, len(lyrics), limit):
                splited_message.append(lyrics[i : i + limit])
                if i > 2:
                    break
            embed.description = splited_message.pop(0)
            await ctx.send_followup(embed=embed)
            for message in splited_message:
                embed.description = message
                await ctx.send(embed=embed)
        else:
            embed.description = lyrics
            await ctx.send_followup(embed=embed)


def setup(bot):
    bot.add_cog(Music(bot))
