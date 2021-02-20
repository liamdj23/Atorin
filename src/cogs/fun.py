from discord.ext import commands
import aiohttp
from random import randrange
from io import BytesIO
import discord
from pyfiglet import Figlet
import unicodedata
from PIL import Image, ImageDraw, ImageFont
import textwrap


class Fun(commands.Cog, name="🎲 Zabawa"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Wpisz aby otrzymać losowe zdjęcie Shiba Inu 🐶")
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
            return
        self.bot.log.error(error)

    @commands.command(usage="<tekst>",
                      description="Stwórz pasek z wiadomości z własnym tekstem\n\nPrzykład użycia: &tvp Atorin jest super!")
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
            return
        self.bot.log.error(error)

    @commands.command(description="Wpisz aby otrzymać losowe zdjęcie kotka")
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
            return
        self.bot.log.error(error)

    @commands.command(description="Wpisz aby otrzymać losowe zdjęcie lisa")
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
            return
        self.bot.log.error(error)

    @commands.command(usage="<tekst>",
                      description="Wpisz aby otrzymać napis stworzony z mniejszych znaków.\n\nPrzykład użycia: &figlet Atorin")
    async def figlet(self, ctx, *, text):
        if not text:
            raise commands.MissingRequiredArgument
        f = Figlet()
        await ctx.send(f"```{f.renderText(text)}```")

    @figlet.error
    async def figlet_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&figlet <tekst>`")
            return
        self.bot.log.error(error)

    @commands.command(description="Jeśli nie masz pomysłu na tytuł commita, skorzystaj z tej komendy")
    async def commit(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://whatthecommit.com/index.txt") as r:
                if r.status == 200:
                    text = await r.text()
                    await ctx.send("git commit -m '{0}'".format(text.replace("\n", "")))
                else:
                    raise commands.CommandError

    @commit.error
    async def commit_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("Nie udało się uzyskać commita. Spróbuj ponownie za chwilę.")
            return
        self.bot.log.error(error)

    @commands.command(usage="<tekst>",
                      description="Stwórz osiągniecie z własnym tekstem\n\nPrzykład użycia: &achievement Jesteś super!",
                      aliases=["achieve", "osiągniecie"])
    async def achievement(self, ctx, *, text):
        if len(text) > 25:
            raise commands.BadArgument
        text = unicodedata.normalize('NFKD', text).replace("ł", "l").replace("Ł", "L").encode('ASCII', 'ignore').decode("UTF-8")
        template = Image.open("assets/achievement/{0}.png".format(randrange(39)))
        d1 = ImageDraw.Draw(template)
        font = ImageFont.truetype("assets/achievement/font.ttf", 16)
        d1.text((60, 7), "Osiagniecie zdobyte!", font=font, fill=(255, 255, 0))
        d1.text((60, 30), text, font=font)
        img = BytesIO()
        template.save(img, "PNG")
        img.seek(0)
        await ctx.send(file=discord.File(img, filename="achievement.png"))

    @achievement.error
    async def achievement_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&achievement <tekst>`")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Zbyt duża ilość znaków, limit to 25 znaków.")
            return
        if isinstance(error, commands.CommandError):
            await ctx.send("Nie udało się wygenerować obrazka. Spróbuj ponownie za chwilę.")
            return
        self.bot.log.error(error)

    @commands.command(usage="<tekst górny | tekst dolny>",
                      description="Stwórz własnego mema z Drake\n\nPrzykład użycia: &drake hawajska | salami")
    async def drake(self, ctx, *, text: str):
        if "|" not in text:
            raise commands.BadArgument
        lines = text.split("|")
        if not len(lines) == 2:
            raise commands.BadArgument
        template = Image.open("assets/drake/template.jpg")
        font = ImageFont.truetype("assets/drake/impact.ttf", 40)
        d1 = ImageDraw.Draw(template)
        offset = 20
        for line in textwrap.wrap(lines[0].strip(), width=15):
            d1.text((360, offset), line, font=font, fill="#000000")
            offset += font.getsize(line)[1]
        offset = 383
        for line in textwrap.wrap(lines[1].strip(), width=15):
            d1.text((360, offset), line, font=font, fill="#000000")
            offset += font.getsize(line)[1]
        img = BytesIO()
        template.save(img, "PNG")
        img.seek(0)
        await ctx.send(file=discord.File(img, filename="drake.png"))

    @drake.error
    async def drake_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&drake <tekst górny | tekst dolny>`")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: `&drake <tekst górny | tekst dolny>`")
            return
        if isinstance(error, commands.CommandError):
            await ctx.send("Nie udało się wygenerować obrazka. Spróbuj ponownie za chwilę.")
            return
        self.bot.log.error(error)

