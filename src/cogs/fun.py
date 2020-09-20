from discord.ext import commands
import aiohttp
from random import randrange
from io import BytesIO
import discord
from pyfiglet import Figlet


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Losowe zdjęcie Shiba Inu",
                      description="Wpisz aby otrzymać losowe zdjęcie Shiba Inu 🐶")
    async def shiba(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://shibe.online/api/shibes?count=1') as r:
                if r.status == 200:
                    data = await r.json()
                    await ctx.send(data[0])
                else:
                    raise commands.CommandError

    @shiba.error
    async def shiba_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("Nie udało się uzyskać obrazka. Spróbuj ponownie za chwilę.")
        self.bot.log.error(error)

    @commands.command(usage="tekst",
                      brief="Generuje pasek w stylu 'Wiadomości'",
                      description="Stwórz pasek z wiadomości z własnym tekstem")
    async def tvp(self, ctx, *, text):
        if len(text) > 48:
            raise commands.BadArgument
        async with aiohttp.ClientSession() as session:
            async with session.post('https://pasek-tvpis.pl/index.php', data={"fimg": randrange(2), "msg": text}) as r:
                if r.status == 200:
                    image = await r.content.read()
                    await ctx.send(file=discord.File(BytesIO(image), filename="tvp.png"))
                else:
                    raise commands.CommandError

    @tvp.error
    async def tvp_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&tvp <tekst>`")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Zbyt duża ilość znaków, limit to 48 znaków.")
            return
        if isinstance(error, commands.CommandError):
            await ctx.send("Nie udało się wygenerować obrazka. Spróbuj ponownie za chwilę.")
        self.bot.log.error(error)

    @commands.command(brief="Losowe zdjęcie kota",
                      description="Wpisz aby otrzymać losowe zdjęcie kotka")
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search?limit=1') as r:
                if r.status == 200:
                    data = await r.json()
                    await ctx.send(data[0]['url'])
                else:
                    raise commands.CommandError

    @cat.error
    async def cat_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("Nie udało się uzyskać obrazka. Spróbuj ponownie za chwilę.")
        self.bot.log.error(error)

    @commands.command(brief="Losowe zdjęcie lisa",
                      description="Wpisz aby otrzymać losowe zdjęcie lisa")
    async def fox(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://randomfox.ca/floof/') as r:
                if r.status == 200:
                    data = await r.json()
                    await ctx.send(data['image'])
                else:
                    raise commands.CommandError

    @fox.error
    async def fox_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("Nie udało się uzyskać obrazka. Spróbuj ponownie za chwilę.")
        self.bot.log.error(error)

    @commands.command(brief="Tworzy figlet", description="Wpisz aby otrzymać napis stworzony z mniejszych znaków.")
    async def figlet(self, ctx, *, text):
        if not text:
            raise commands.MissingRequiredArgument
        f = Figlet()
        await ctx.send(f"```{f.renderText(text)}```")

    @figlet.error
    async def figlet_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&figlet <tekst>`")
