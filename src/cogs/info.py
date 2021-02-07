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

    @commands.command(brief="Link do bota i serwera supportu",
                      description="Wpisz aby zaprosić Atorina na swój serwer lub uzyskać wsparcie")
    async def invite(self, ctx):
        await ctx.send("🔹 Dodaj Atorina na swój serwer, korzystając z tego linku:\n <https://liamdj23.ovh/addbot>")

    @commands.command(brief="Informacje o serwerze",
                      description="Wpisz aby otrzymać informacje o serwerze")
    @commands.guild_only()
    async def server(self, ctx):
        guild = ctx.guild
        embed = await self.bot.embed()
        embed.title = "Informacje o " + guild.name
        embed.add_field(name="🆔 ID", value=guild.id)
        embed.add_field(name="🌍 Region", value=guild.region)
        embed.add_field(name="💬 Liczba kanałów", value=len(guild.channels))
        embed.add_field(name="👥 Liczba członków", value=guild.member_count)
        embed.add_field(name="👶 Data utworzenia", value=guild.created_at.replace(microsecond=0))
        embed.set_thumbnail(url=guild.icon_url)
        await ctx.send(embed=embed)

    @server.error
    async def server_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tej komendy można użyć tylko na serwerze!")
            return
        self.bot.log.error(error)

    @commands.command(aliases=["pogoda"], brief="Pogoda w Twojej miejscowości",
                      description="Wpisz aby otrzymać aktualną pogodę w Twojej miejscowości")
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
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Nie znaleziono podanej miejscowości.")
            return
        if isinstance(error, commands.CommandError):
            await ctx.send("❌ Wystąpił błąd, spróbuj ponownie później.")
            return
        self.bot.log.error(error)

    @commands.command(brief="Informacje o Atorinie",
                      description="Wpisz aby otrzymać informacje o Atorinie")
    async def bot(self, ctx):
        embed = await self.bot.embed()
        embed.title = "Informacje o AtorinBot"
        embed.add_field(name="🌐 Liczba serwerów", value=len(self.bot.guilds))
        embed.add_field(name="👨‍💻 Autor", value="liamdj23#9081")
        embed.add_field(name="🎭 Discord", value="https://discord.gg/Ygr5wAZbsZ", inline=False)
        embed.add_field(name="📄 Panel zarządzania", value="https://bot.liamdj23.ovh/panel", inline=False)
        cp = psutil.Process()
        embed.add_field(name="🖥 Użycie zasobów", inline=False, value="```css\n{0}\n{1}```".format(
            progress_bar(int(cp.cpu_percent()), "CPU"),
            progress_bar(int(cp.memory_percent()), "RAM")))
        await ctx.send(embed=embed)





