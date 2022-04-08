import time
from urllib.parse import quote
import platform
from datetime import datetime, timedelta

import aiohttp
from bs4 import BeautifulSoup
import discord
import psutil
import humanize
from discord.ext import commands
from discord.commands import slash_command, Option, OptionChoice
import httpx

from atorin.bot import Atorin
from .. import config
from ..utils import get_weather_emoji, progress_bar, convert_size, user_counter


class HelpButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(emoji="💵", label="Wsparcie", url="https://buycoffee.to/liamdj23"))
        self.add_item(discord.ui.Button(emoji="🚑", label="Discord", url="https://liamdj23.ovh/discord"))


class Info(commands.Cog, name="ℹ Informacje"):
    def __init__(self, bot: Atorin):
        self.bot = bot

    @slash_command(
        description="User profile picture",
        description_localizations={"pl": "Zdjęcie profilowe użytkownika"},
        guild_ids=config["guild_ids"],
    )
    async def avatar(
        self,
        ctx: discord.ApplicationContext,
        user: Option(
            discord.User,
            name="user",
            name_localizations={"pl": "osoba"},
            description="Select user whose avatar you want to see",
            description_localizations={"pl": "Osoba, której awatar chcesz zobaczyć"},
            required=False,
        ),
    ):
        if not user:
            user = ctx.author
        if type(user) is int:
            user = await self.bot.fetch_user(user)
            if not user:
                raise commands.BadArgument(
                    "Nie znaleziono użytkownika!" if ctx.interaction.locale == "pl" else "User not found!"
                )
        embed = discord.Embed()
        embed.title = f"Zdjęcie profilowe {user}" if ctx.interaction.locale == "pl" else f"{user}'s profile picture"
        embed.set_image(url=user.display_avatar.url)
        await ctx.respond(embed=embed)

    @slash_command(
        description="Informations about guild",
        description_localizations={"pl": "Informacje o serwerze"},
        guild_ids=config["guild_ids"],
    )
    @commands.guild_only()
    async def server(self, ctx: discord.ApplicationContext):
        guild = ctx.guild
        embed = discord.Embed()
        embed.title = f"Informacje o {guild}" if ctx.interaction.locale == "pl" else f"Informations about {guild}"
        if guild.owner:
            embed.add_field(
                name="👑 Właściciel" if ctx.interaction.locale == "pl" else "👑 Owner", value=f"{guild.owner.mention}"
            )
        if guild.description:
            embed.add_field(
                name="🔤 Opis" if ctx.interaction.locale == "pl" else "🔤 Description",
                value=f"**{guild.description}**",
                inline=False,
            )
        embed.add_field(
            name="👶 Data utworzenia" if ctx.interaction.locale == "pl" else "👶 Created at",
            value=f"<t:{int(datetime.timestamp(guild.created_at))}>",
        )
        embed.add_field(name="🆔 ID", value=f"`{guild.id}`")
        embed.add_field(
            name="📊 Statystyki" if ctx.interaction.locale == "pl" else "📊 Statistics",
            value=f"**💬 {'Liczba kanałów' if ctx.interaction.locale == 'pl' else 'Channels'}: `{len(guild.channels)}`\n👥 {'Liczba członków' if ctx.interaction.locale == 'pl' else 'Members'}: `{guild.member_count}`\n🤪 {'Liczba emotek' if ctx.interaction.locale == 'pl' else 'Emotes'}: `{len(guild.emojis) if guild.emojis else 0}`\n🚀 {'Liczba ulepszeń' if ctx.interaction.locale == 'pl' else 'Boosts'}: `{guild.premium_subscription_count}`\n📛 {'Liczba ról' if ctx.interaction.locale == 'pl' else 'Roles'}: `{len(guild.roles)}`**",
            inline=False,
        )
        embed.set_thumbnail(url=str(guild.icon))
        await ctx.respond(embed=embed)

    @slash_command(
        description="Informations about user",
        description_localizations={"pl": "Informacje o użytkowniku"},
        guild_ids=config["guild_ids"],
    )
    async def user(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            discord.Member,
            name="member",
            name_localizations={"pl": "użytkownik"},
            description="Select user you want information about",
            description_localizations={"pl": "Osoba której informacje chcesz wyświetlić"},
            required=False,
        ),
    ):
        if member is None:
            member = ctx.author
        embed = discord.Embed()
        embed.title = f"Informacje o {member}" if ctx.interaction.locale == "pl" else f"Informations about {member}"
        embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=False)
        if member.nick:
            embed.add_field(name="🎭 Pseudonim" if ctx.interaction.locale == "pl" else "🎭 Nickname", value=member.nick)
        embed.add_field(
            name="🏅 Role" if ctx.interaction.locale == "pl" else "🏅 Roles",
            value=", ".join(role.mention for role in member.roles),
            inline=False,
        )
        embed.add_field(
            name="👶 Data utworzenia konta" if ctx.interaction.locale == "pl" else "👶 Created at",
            value=f"<t:{int(datetime.timestamp(member.created_at))}>",
        )
        embed.add_field(
            name="🤝 Data dołączenia" if ctx.interaction.locale == "pl" else "🤝 Joined at",
            value=f"<t:{int(datetime.timestamp(member.joined_at))}>",
        )
        embed.set_thumbnail(url=str(member.display_avatar))
        await ctx.respond(embed=embed)

    @slash_command(
        description="Check weather forecast in your city",
        description_localizations={"pl": "Sprawdź pogodę w Twojej miejscowości"},
        guild_ids=config["guild_ids"],
    )
    async def weather(
        self,
        ctx: discord.ApplicationContext,
        city: Option(
            str,
            name="city",
            name_localizations={"pl": "miejscowość"},
            description="Type city name or postal code",
            description_localizations={"pl": "Podaj nazwę miejscowości lub kod pocztowy"},
        ),
    ):
        token = config["weather"]
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "http://api.openweathermap.org/data/2.5/weather",
                params={
                    "appid": token,
                    "units": "metric",
                    "lang": "pl" if ctx.interaction.locale == "pl" else "en",
                    "q": city,
                },
            )
        embed = discord.Embed()
        if r.status_code == 200:
            data = r.json()
            embed.title = (
                f"Pogoda w {data['name']}" if ctx.interaction.locale == "pl" else f"Weather in {data['name']}"
            )
            emoji = get_weather_emoji(data["weather"][0]["id"])
            embed.description = f"{emoji} __**{data['weather'][0]['description'].capitalize()}**__"
            embed.add_field(
                name="🌡️ Temperatura" if ctx.interaction.locale == "pl" else "🌡️ Temperature",
                value=f"{data['main']['temp']}°C",
            )
            embed.add_field(
                name="👐 Odczuwalna" if ctx.interaction.locale == "pl" else "👐 Feels like",
                value=f"{data['main']['feels_like']}°C",
            )
            embed.add_field(
                name="🥶 Najniższa" if ctx.interaction.locale == "pl" else "🥶 Low",
                value=f"{data['main']['temp_min']}°C",
            )
            embed.add_field(
                name="🥵 Najwyższa" if ctx.interaction.locale == "pl" else "🥵 High",
                value=f"{data['main']['temp_max']}°C",
            )
            embed.add_field(
                name="🎈 Ciśnienie" if ctx.interaction.locale == "pl" else "🎈 Pressure",
                value=f"{data['main']['pressure']}hPa",
            )
            embed.add_field(
                name="💧 Wilgotność" if ctx.interaction.locale == "pl" else "💧 Humidity",
                value=f"{data['main']['humidity']}%",
            )
            embed.add_field(
                name="💨 Wiatr" if ctx.interaction.locale == "pl" else "💨 Wind",
                value=f"{int(data['wind']['speed'] * 3.6)}km/h",
            )
            embed.add_field(
                name="🌅 Wschód słońca" if ctx.interaction.locale == "pl" else "🌅 Sunrise",
                value=f"<t:{data['sys']['sunrise']}:t>",
            )
            embed.add_field(
                name="🌇 Zachód słońca" if ctx.interaction.locale == "pl" else "🌇 Sunset",
                value=f"<t:{data['sys']['sunset']}:t>",
            )
            await ctx.send_followup(embed=embed)
        elif r.status_code == 404:
            raise commands.BadArgument(
                "Nie odnaleziono podanej miejscowości!" if ctx.interaction.locale == "pl" else "City not found!"
            )
        else:
            raise commands.CommandError(
                f"Wystąpił błąd przy pobieraniu prognozy pogody, spróbuj ponownie później. [{r.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while downloading weather forecast, try again later. [{r.status_code}]"
            )

    @slash_command(
        description="Informations about Atorin",
        description_localizations={"pl": "Informacje o Atorinie"},
        guild_ids=config["guild_ids"],
    )
    async def bot(self, ctx: discord.ApplicationContext):
        if hasattr(self.bot, "lavalink") and self.bot.lavalink.node_manager.nodes[0].stats:
            lavalink_stats = self.bot.lavalink.node_manager.nodes[0].stats.playing_players
        else:
            lavalink_stats = "Niedostępne" if ctx.interaction.locale == "pl" else "Unavailable"
        embed = discord.Embed()
        embed.title = "Informacje o Atorinie" if ctx.interaction.locale == "pl" else "Informations about Atorin"
        embed.description = f"**👨‍💻 {'Autor' if ctx.interaction.locale == 'pl' else 'Author'}: <@272324980522614784>**"
        embed.add_field(
            name=f"🌐 {'Liczba serwerów' if ctx.interaction.locale == 'pl' else 'Servers'}: {len(self.bot.guilds)}",
            value=f"**#️⃣ {'Liczba kanałów' if ctx.interaction.locale == 'pl' else 'Channels'}: {len(list(self.bot.get_all_channels()))}\n🧑‍🤝‍🧑 {'Liczba użytkowników' if ctx.interaction.locale == 'pl' else 'Users'}: {sum(user_counter(self.bot))}\n🎵 {'Liczba odtwarzaczy' if ctx.interaction.locale == 'pl' else 'Players'}: {lavalink_stats}\n⏱ Uptime: {humanize.naturaldelta(timedelta(seconds=self.bot.get_uptime()))}**",
        )
        embed.add_field(
            name="⚙️ Środowisko" if ctx.interaction.locale == "pl" else "⚙️ Environment",
            value=f"Atorin: `{self.bot.get_version()}`\nPython: `{platform.python_version()}`\nOS: `{platform.system()}`\nPy-cord: `{discord.__version__}`",
        )
        ram = psutil.virtual_memory()
        total_ram = convert_size(ram.total)
        used_ram = convert_size(ram.used)
        disk = psutil.disk_usage("/")
        total_disk = convert_size(disk.total)
        used_disk = convert_size(disk.used)
        embed.add_field(
            name="🖥 Użycie zasobów" if ctx.interaction.locale == "pl" else "🖥 Resource usage",
            inline=False,
            value=f"```css\n{progress_bar(int(psutil.cpu_percent()), 'CPU')}\n{progress_bar(int((ram.used / ram.total) * 100), f'RAM {used_ram}/{total_ram}')}\n{progress_bar(int(disk.percent), f'Dysk {used_disk}/{total_disk}' if ctx.interaction.locale == 'pl' else f'Disk {used_disk}/{total_disk}')}```",
        )
        await ctx.respond(embed=embed)

    @slash_command(
        description="List of Atorin commands",
        description_localizations={"pl": "Lista komend Atorina"},
        guild_ids=config["guild_ids"],
    )
    async def help(self, ctx: discord.ApplicationContext):
        embed = discord.Embed()
        embed.title = "Lista komend AtorinBot" if ctx.interaction.locale == "pl" else "List of Atorin commands"
        for name, cog in self.bot.cogs.items():
            embed.add_field(name=name, value=f"`{', '.join([c.name for c in cog.get_commands()])}`")
        buttons = HelpButtons()
        await ctx.respond(embed=embed, view=buttons)

    @slash_command(
        description="Donations",
        description_localizations={"pl": "Wsparcie bota"},
        guild_ids=config["guild_ids"],
    )
    async def support(self, ctx: discord.ApplicationContext):
        embed = discord.Embed()
        embed.title = "Wsparcie bota" if ctx.interaction.locale == "pl" else "Donations"
        embed.description = (
            "💵 Jeśli chcesz wesprzeć rozwój Atorina, możesz postawić kawę jego twórcy na stronie https://buycoffee.to/liamdj23\n**Dziękuję.**"
            if ctx.interaction.locale == "pl"
            else "💵 If you want to support the development of Atorin, buy the author a coffee on https://buycoffee.to/liamdj23\n**Thank you.**"
        )
        embed.add_field(
            name="🎉 Wspierający 🎉" if ctx.interaction.locale == "pl" else "🎉 Special thanks to 🎉",
            value="`Leaf#7075, KMatuszak#2848, Golden_Girl00#0055, HunterAzar#1387, koosek#2618, Vretu#2855`",
        )
        buttons = HelpButtons()
        await ctx.respond(embed=embed, view=buttons)

    async def surname_searcher(self, ctx: discord.AutocompleteContext):
        if not ctx.value or len(ctx.value) < 2:
            return []
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://nazwiska.ijp.pan.pl/public/backend/nwp/ajax/hasla-tab-slownik-starts.php",
                params={"query": ctx.value.lower()},
                headers={"User-agent": "Atorin"},
            )
        if r.status_code != 200:
            return []
        data = r.json()["aaData"]
        return [OptionChoice(name=entry["nazwisko"].lower().capitalize(), value=entry["menuID"]) for entry in data]

    @slash_command(
        description="Informations about surnames in Poland",
        description_localizations={"pl": "Nazwiska w Polsce"},
        guild_ids=config["guild_ids"],
    )
    async def surnames(
        self,
        ctx: discord.ApplicationContext,
        surname: Option(
            str,
            name="surname",
            name_localizations={"pl": "nazwisko"},
            description="Type surname you want information about",
            description_localizations={"pl": "Podaj nazwisko, o którym chcesz uzyskać informacje"},
            autocomplete=surname_searcher,
        ),
    ):
        await ctx.defer()
        if not surname.isdigit():
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    "https://nazwiska.ijp.pan.pl/public/backend/nwp/ajax/hasla-tab-slownik-starts.php",
                    params={"query": surname},
                    headers={"User-agent": "Atorin"},
                )
                if r.status_code != 200:
                    raise commands.CommandError(
                        f"Wystąpił błąd przy pobieraniu nazwisk, spróbuj ponownie później. [{r.status_code}]"
                        if ctx.interaction.locale == "pl"
                        else f"Error has occurred while downloading surnames, try again later. [{r.status_code}]"
                    )
            data = r.json()["aaData"]
            if not data:
                raise commands.BadArgument(
                    "Nie znaleziono podanego nazwiska!" if ctx.interaction.locale == "pl" else "Surname not found!"
                )
            surname = data[0]["menuID"]
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"https://nazwiska.ijp.pan.pl/haslo/show/id/{surname.strip()}",
                headers={"User-agent": "Atorin"},
            )
            if r.status_code != 200:
                raise commands.CommandError(
                    f"Wystąpił błąd przy pobieraniu informacji o nazwisku, spróbuj ponownie później. [{r.status_code}]"
                    if ctx.interaction.locale == "pl"
                    else f"Error has occurred while downloading informations about surname, try again later. [{r.status_code}]"
                )
        soup = BeautifulSoup(r.content, "html.parser")
        embed = discord.Embed()
        embed.title = "Nazwiska w Polsce" if ctx.interaction.locale == "pl" else "Surnames in Poland"
        embed.description = f"🧑 **{'Nazwisko' if ctx.interaction.locale == 'pl' else 'Surname'}: {soup.find('h1', class_='title').text.lower().capitalize()}**\n{soup.find(id='collapse-liczba').text.strip()}"
        voivodships = soup.find(id="collapse-geografia").text.strip().split("\n\n\n\n")[0].split("\n")[2:]
        for i, _ in enumerate(voivodships):
            name, count = voivodships[i].split(" /")
            voivodships[i] = f"{name.lower().capitalize()}: **{count}**"
        counties = soup.find(id="collapse-geografia").text.strip().split("\n\n\n\n")[1].split("\n")[2:]
        for i, _ in enumerate(counties):
            name, count = counties[i].split(" /")
            counties[i] = f"{name.lower().capitalize()}: **{count}**"
        municipalities = soup.find(id="collapse-geografia").text.strip().split("\n\n\n\n")[2].split("\n")[2:]
        for i, _ in enumerate(municipalities):
            name, count = municipalities[i].split(" /")
            municipalities[i] = f"{name.lower().capitalize()}: **{count}**"
        embed.add_field(
            name="🏢 Województwa" if ctx.interaction.locale == "pl" else "🏢 Voivodships",
            value="\n".join(voivodships),
        )
        embed.add_field(
            name="🏘️ Powiaty" if ctx.interaction.locale == "pl" else "🏘️ Counties", value="\n".join(counties)
        )
        embed.add_field(
            name="🏡 Gminy" if ctx.interaction.locale == "pl" else "🏡 Municipalities",
            value="\n".join(municipalities),
        )
        embed.set_footer(text=f"{'Źródło' if ctx.interaction.locale == 'pl' else 'Source'}: nazwiska.ijp.pan.pl")
        await ctx.send_followup(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
