from discord.ext import commands
import aiohttp


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
