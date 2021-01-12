from discord.ext import commands
import discord
from io import BytesIO
import aiohttp
from urllib.parse import quote
from utils import get_weather_emoji, progress_bar
import psutil


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def avatar(self, ctx, *, user: discord.User):
        avatar = await user.avatar_url.read()
        await ctx.send(file=discord.File(BytesIO(avatar), filename=user.name + ".png"))

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&avatar @użytkownik`")
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Nie znaleziono użytkownika o podanej nazwie.")
        if isinstance(error, discord.HTTPException):
            await ctx.send("❌ Wystąpił błąd przy pobieraniu avatara, spróbuj ponownie.")
        self.bot.log.error(error)

    @commands.command()
    async def invite(self, ctx):
        await ctx.send("🔹 Dodaj Atorina na swój serwer, korzystając z tego linku:\n <https://liamdj23.ovh/addbot>")

    @commands.command()
    @commands.guild_only()
    async def user(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = await self.bot.embed()
        embed.title = "Informacje o " + member.name + "#" + member.discriminator
        embed.add_field(name="🆔 ID", value=member.id)
        embed.add_field(name="🎭 Pseudonim", value=member.nick)
        embed.add_field(name="👶 Data utworzenia konta", value=member.created_at.replace(microsecond=0), inline=False)
        embed.add_field(name="🤝 Data dołączenia", value=member.joined_at.replace(microsecond=0))
        roles = ""
        for role in member.roles:
            roles += role.mention + ","
        embed.add_field(name="🏅 Role", value=roles)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def server(self, ctx):
        guild = ctx.guild
        embed = await self.bot.embed()
        embed.title = "Informacje o " + guild.name
        embed.add_field(name="🆔 ID", value=guild.id)
        embed.add_field(name="🌍 Region", value=guild.region)
        embed.add_field(name="💬 Liczba kanałów", value=len(guild.channels))
        embed.add_field(name="👥 Liczba członków", value=guild.member_count)
        embed.add_field(name="👑 Właściciel", value=guild.owner)
        embed.add_field(name="👶 Data utworzenia", value=guild.created_at.replace(microsecond=0))
        embed.set_thumbnail(url=guild.icon_url)
        await ctx.send(embed=embed)

    @server.error
    async def server_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tej komendy można użyć tylko na serwerze!")
        self.bot.log.error(error)

    @commands.command(aliases=["pogoda"])
    async def weather(self, ctx, *, city: str):
        token = self.bot.mongo.Token.objects(id="weather").first().key
        async with aiohttp.ClientSession() as session:
            async with session.get('http://api.openweathermap.org/data/2.5/weather?appid={0}&units=metric&lang=pl&q={1}'
                                   .format(token, quote(city))) as r:
                if r.status == 200:
                    data = await r.json()
                    if "message" in data:
                        if data["message"] == "city not found":
                            raise commands.BadArgument
                    embed = await self.bot.embed()
                    embed.title = "Pogoda w " + data["name"]
                    emoji = get_weather_emoji(data["weather"][0]["id"])
                    embed.add_field(name=emoji + " Pogoda", value=data["weather"][0]["description"])
                    embed.add_field(name="🌡️ Temperatura", value=str(data["main"]["temp"]) + "°C", inline=False)
                    embed.add_field(name="🎈 Ciśnienie", value=str(data["main"]["pressure"]) + "hPa")
                    embed.add_field(name="💧 Wilgotność", value=str(data["main"]["humidity"]) + "%")
                    embed.add_field(name="💨 Wiatr", value=str(data["wind"]["speed"]) + "m/s")
                    await ctx.send(embed=embed)
                else:
                    raise commands.CommandError

    @weather.error
    async def weather_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&pogoda <miejscowość>`")
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Nie znaleziono podanej miejscowości.")
        if isinstance(error, commands.CommandError):
            await ctx.send("❌ Wystąpił błąd, spróbuj ponownie później.")
        self.bot.log.error(error)

    @commands.command()
    async def bot(self, ctx):
        embed = await self.bot.embed()
        embed.title = "Informacje o AtorinBot"
        embed.add_field(name="🌐 Liczba serwerów", value=len(self.bot.guilds))
        # embed.add_field(name="👥 Użytkownicy", value=len(self.bot.users))
        embed.add_field(name="👨‍💻 Autor", value="liamdj23#9081")
        embed.add_field(name="📄 Panel zarządzania", value="https://bot.liamdj23.ovh/panel", inline=False)
        cp = psutil.Process()
        embed.add_field(name="🖥 Użycie zasobów", inline=False, value="```css\n{0}\n{1}```".format(
            progress_bar(int(cp.cpu_percent()), "CPU"),
            progress_bar(int(cp.memory_percent()), "RAM")))
        await ctx.send(embed=embed)





