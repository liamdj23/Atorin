from urllib.parse import quote
import platform
from datetime import datetime

import aiohttp
import discord
import psutil
from discord.ext import commands
from discord.commands import slash_command, Option

from atorin.bot import Atorin
from .. import config
from ..utils import get_weather_emoji, progress_bar, convert_size, user_counter


class HelpButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(
            discord.ui.Button(label="Wsparcie", url="https://buycoffee.to/liamdj23")
        )
        self.add_item(
            discord.ui.Button(label="Discord", url="https://liamdj23.ovh/discord")
        )


class Info(commands.Cog, name="ℹ Informacje"):
    def __init__(self, bot: Atorin):
        self.bot = bot

    @slash_command(
        description="Zdjęcie profilowe użytkownika", guild_ids=[408960275933429760]
    )
    async def avatar(
        self,
        ctx: discord.ApplicationContext,
        user: Option(
            discord.Member,
            "Nazwa osoby której awatar chcesz wyświetlić",
            required=False,
        ),
    ):
        if not user:
            user = ctx.author
        embed = discord.Embed()
        embed.title = f"Zdjęcie profilowe {user}"
        embed.set_image(url=user.display_avatar.url)
        await ctx.respond(embed=embed)

    @slash_command(description="Informacje o serwerze", guild_ids=[408960275933429760])
    @commands.guild_only()
    async def server(self, ctx: discord.ApplicationContext):
        guild = ctx.guild
        embed = discord.Embed()
        embed.title = f"Informacje o {guild}"
        if guild.owner:
            embed.add_field(name="👑 Właściciel", value=f"{guild.owner.mention}")
        embed.add_field(
            name="🔤 Opis",
            value=f"**{guild.description if guild.description else 'Brak'}**",
            inline=False,
        )
        embed.add_field(
            name="👶 Data utworzenia",
            value=f"<t:{int(datetime.timestamp(guild.created_at))}>",
        )
        embed.add_field(name="🆔 ID", value=f"`{guild.id}`", inline=False)
        embed.add_field(
            name="📊 Statystyki",
            value=f"**💬 Liczba kanałów: `{len(guild.channels)}`\n👥 Liczba członków: `{guild.member_count}`\n🤪 Liczba emotek: `{len(guild.emojis) if guild.emojis else 0}`\n🚀 Liczba ulepszeń: `{guild.premium_subscription_count}`\n📛 Liczba ról: `{len(guild.roles)}`**",
            inline=False,
        )
        embed.set_thumbnail(url=str(guild.icon))
        await ctx.respond(embed=embed)

    @slash_command(
        description="Informacje o użytkowniku", guild_ids=[408960275933429760]
    )
    async def user(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            discord.Member,
            "Osoba której informacje chcesz wyświetlić",
            required=False,
        ),
    ):
        if member is None:
            member = ctx.author
        embed = discord.Embed()
        embed.title = f"Informacje o {member}"
        embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=False)
        if member.nick:
            embed.add_field(name="🎭 Pseudonim", value=member.nick)
        embed.add_field(
            name="🏅 Role",
            value=", ".join(role.mention for role in member.roles),
            inline=False,
        )
        embed.add_field(
            name="👶 Data utworzenia konta",
            value=f"<t:{int(datetime.timestamp(member.created_at))}>",
        )
        embed.add_field(
            name="🤝 Data dołączenia",
            value=f"<t:{int(datetime.timestamp(member.joined_at))}>",
        )
        embed.set_thumbnail(url=str(member.display_avatar))
        await ctx.respond(embed=embed)

    @slash_command(
        description="Sprawdź pogodę w Twojej miejscowości",
        guild_ids=[408960275933429760],
    )
    async def weather(
        self,
        ctx: discord.ApplicationContext,
        city: Option(str, "Miejscowość lub kod pocztowy"),
    ):
        token = config["weather"]
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://api.openweathermap.org/data/2.5/weather?appid={0}&units=metric&lang=pl&q={1}".format(
                    token, quote(city)
                )
            ) as r:
                embed = discord.Embed()
                if r.status == 200:
                    data = await r.json()
                    embed.title = "Pogoda w " + data["name"]
                    emoji = get_weather_emoji(data["weather"][0]["id"])
                    embed.description = f"{emoji} __**{data['weather'][0]['description'].capitalize()}**__"
                    embed.add_field(
                        name="🌡️ Temperatura",
                        value=f"{data['main']['temp']}°C",
                    )
                    embed.add_field(
                        name="👐 Odczuwalna",
                        value=f"{data['main']['feels_like']}°C",
                    )
                    embed.add_field(
                        name="🥶 Najniższa",
                        value=f"{data['main']['temp_min']}°C",
                    )
                    embed.add_field(
                        name="🥵 Najwyższa",
                        value=f"{data['main']['temp_max']}°C",
                    )
                    embed.add_field(
                        name="🎈 Ciśnienie",
                        value=f"{data['main']['pressure']}hPa",
                    )
                    embed.add_field(
                        name="💧 Wilgotność",
                        value=f"{data['main']['humidity']}%",
                    )
                    embed.add_field(
                        name="💨 Wiatr",
                        value=f"{int(data['wind']['speed'] * 3.6)}km/h",
                    )
                    embed.add_field(
                        name="🌅 Wschód słońca",
                        value=f"<t:{data['sys']['sunrise']}:t>",
                    )
                    embed.add_field(
                        name="🌇 Zachód słońca",
                        value=f"<t:{data['sys']['sunset']}:t>",
                    )
                    await ctx.send_followup(embed=embed)
                elif r.status == 404:
                    raise commands.BadArgument("Nie odnaleziono podanej miejscowości.")
                else:
                    raise commands.CommandError(await r.text())

    @slash_command(description="Informacje o Atorinie", guild_ids=[408960275933429760])
    async def bot(self, ctx: discord.ApplicationContext):
        if (
            hasattr(self.bot, "lavalink")
            and self.bot.lavalink.node_manager.nodes[0].stats
        ):
            lavalink_stats = self.bot.lavalink.node_manager.nodes[
                0
            ].stats.playing_players
        else:
            lavalink_stats = "Niedostępne"
        embed = discord.Embed()
        embed.title = "Informacje o Atorinie"
        embed.description = "**👨‍💻 Autor: <@272324980522614784>**"
        embed.add_field(
            name=f"🌐 Liczba serwerów: {len(self.bot.guilds)}",
            value=f"**#️⃣ Liczba kanałów: {len(list(self.bot.get_all_channels()))}\n🧑‍🤝‍🧑 Liczba użytkowników: {sum(user_counter(self.bot))}\n🎵 Liczba odtwarzaczy: {lavalink_stats}**",
        )
        embed.add_field(
            name="⚙️ Środowisko",
            value=f"Python: `{platform.python_version()}`\nOS: `{platform.system()}`\nPy-cord: `{discord.__version__}`",
        )
        ram = psutil.virtual_memory()
        total_ram = convert_size(ram.total)
        used_ram = convert_size(ram.used)
        disk = psutil.disk_usage("/")
        total_disk = convert_size(disk.total)
        used_disk = convert_size(disk.used)
        embed.add_field(
            name="🖥 Użycie zasobów",
            inline=False,
            value="```css\n{0}\n{1}\n{2}```".format(
                progress_bar(int(psutil.cpu_percent()), "CPU"),
                progress_bar(
                    int((ram.used / ram.total) * 100),
                    "RAM {}/{}".format(used_ram, total_ram),
                ),
                progress_bar(
                    int(disk.percent), "Dysk {}/{}".format(used_disk, total_disk)
                ),
            ),
        )
        await ctx.respond(embed=embed)

    @slash_command(description="Lista komend AtorinBot", guild_ids=[408960275933429760])
    async def help(self, ctx: discord.ApplicationContext):
        embed = discord.Embed()
        embed.title = "Lista komend AtorinBot"
        for name, cog in self.bot.cogs.items():
            embed.add_field(
                name=name, value=f"`{', '.join([c.name for c in cog.get_commands()])}`"
            )
        buttons = HelpButtons()
        await ctx.respond(embed=embed, view=buttons)

    @slash_command(
        description="Wsparcie bota",
        guild_ids=[408960275933429760],
    )
    async def support(self, ctx: discord.ApplicationContext):
        embed = discord.Embed()
        embed.title = "Wsparcie bota"
        embed.description = "☕️ Jeśli chcesz wesprzeć rozwój Atorina, możesz postawić kawę jego twórcy na stronie https://buycoffee.to/liamdj23\n**Dziękuję.**"
        embed.add_field(
            name="🎉 Wspierający 🎉",
            value="`Leaf#7075, KMatuszak#2848, Golden_Girl00#0055, HunterAzar#1387, koosek#2618, Vretu#2855`",
        )
        buttons = HelpButtons()
        await ctx.respond(embed=embed, view=buttons)


def setup(bot):
    bot.add_cog(Info(bot))
