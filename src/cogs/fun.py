from discord.ext import commands
import aiohttp
from random import randrange
from io import BytesIO
import discord


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Losowe zdjęcie Shiba Inu", description="Wpisz aby otrzymać losowe zdjęcie Shiba Inu 🐶")
    async def shiba(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://shibe.online/api/shibes?count=1') as r:
                if r.status == 200:
                    data = await r.json()
                    await ctx.send(data[0])

    @commands.command(usage="tekst")
    async def tvp(self, ctx, *, text):
        if len(text) > 48:
            raise commands.BadArgument
        async with aiohttp.ClientSession() as session:
            async with session.post('https://pasek-tvpis.pl/index.php', data={"fimg": randrange(2), "msg": text}) as r:
                if r.status == 200:
                    image = await r.content.read()
                    await ctx.send(file=discord.File(BytesIO(image), filename="tvp.png"))

    @tvp.error
    async def tvp_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&tvp <tekst>`")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Zbyt duża ilość znaków, limit to 48 znaków.")
            return
        print("TVP: " + error)
