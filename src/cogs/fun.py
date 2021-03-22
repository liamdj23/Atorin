import textwrap
import unicodedata
from io import BytesIO
from random import randrange

import aiohttp
import discord
import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from pyfiglet import Figlet


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

    @commands.command(description="Wpisz aby otrzymać losowe zdjęcie kotka", aliases=["kot"])
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

    @commands.command(description="Wpisz aby otrzymać losowe zdjęcie lisa", aliases=["lis"])
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

    @commands.command(usage="<tekst lub link>",
                      description="Utwórz własny kod QR z tekstem lub linkiem\n\nPrzykład użycia: &qr liamdj23.ovh/addbot",
                      aliases=["kodqr", "qr"])
    async def codeqr(self, ctx, *, content: str):
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(content)
        qr.make(fit=True)
        code = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        logo = Image.open("assets/qrcode/logo.png")
        logo.thumbnail((60, 60))
        logo_pos = ((code.size[0] - logo.size[0]) // 2, (code.size[1] - logo.size[1]) //2)
        code.paste(logo, logo_pos)
        img = BytesIO()
        code.save(img, "PNG")
        img.seek(0)
        await ctx.send(file=discord.File(img, filename="qr.png"))

    @codeqr.error
    async def codeqr_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&qr <tekst lub link>`")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: `&qr <tekst lub link>`")
            return
        if isinstance(error, commands.CommandError):
            await ctx.send("Nie udało się wygenerować kodu QR. Spróbuj ponownie za chwilę.")
            return
        self.bot.log.error(error)

    @commands.command(usage="<nazwa>",
                      description="Pokazuje profil z Instagrama",
                      aliases=["ig"])
    async def instagram(self, ctx, name: str):
        cookies = []
        for cookie in self.bot.config["instagram"]:
            cookies.append(cookie["name"]+"="+cookie["value"])
        r = requests.get("https://www.instagram.com/{}/?__a=1".format(name.replace("@", "")), headers={
            "cookie": "; ".join(cookies)
        })
        if r.status_code == 404:
            await ctx.send("❌ Nie znaleziono użytkownika o podanej nazwie")
            return
        data = r.json()
        if not data["graphql"]:
            raise commands.CommandError
        embed = self.bot.embed(ctx.author)
        user = data["graphql"]["user"]
        embed.title = "Profil {} na Instagramie".format(user["username"])
        if user["full_name"]:
            embed.add_field(name="😊 Pełna nazwa", value=user["full_name"], inline=False)
        if not user["is_private"]:
            embed.add_field(name="🔑 Prywatne", value="Nie")
        else:
            embed.add_field(name="🔑 Prywatne", value="Tak")
        if user["biography"]:
            embed.add_field(name="📝 Opis", value="```yml\n{}```".format(user["biography"]), inline=False)
        embed.add_field(name="😍 Obserwujących", value=str(user["edge_followed_by"]["count"]))
        embed.add_field(name="👀 Obserwuje", value=str(user["edge_follow"]["count"]))
        embed.add_field(name="🔗 Link", value="https://instagram.com/{}".format(user["username"]), inline=False)
        if user["profile_pic_url_hd"]:
            embed.set_thumbnail(url=user["profile_pic_url_hd"])
        await ctx.send(embed=embed)

    @instagram.error
    async def instagram_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("❌ Wystąpił błąd wewnętrzny, spróbuj ponownie później.")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie `&ig <nazwa>`")
            return

    @commands.command(usage="@poszukiwany",
                      description="Oznacz kogoś aby stał się poszukiwany\n\nPrzykład użycia: &wanted @liamdj23",
                      aliases=["poszukiwany"])
    async def wanted(self, ctx, *, user: discord.User):
        template = Image.open("assets/wanted/wanted.jpg")
        avatar = Image.open(BytesIO(await user.avatar_url.read()))
        avatar_resized = avatar.resize((320, 320))
        w, h = avatar_resized.size
        template.paste(avatar_resized, (44, 123, 44+w, 123+h))
        img = BytesIO()
        template.save(img, "PNG")
        img.seek(0)
        await ctx.send(file=discord.File(img, filename="wanted.png"))

    @wanted.error
    async def wanted_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&wanted @poszukiwany`")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: &wanted @poszukiwany`")
            return
        if isinstance(error, commands.UserNotFound):
            await ctx.send("❌ Nie znaleziono podanego użytkownika.")
            return
        if isinstance(error, commands.CommandError):
            await ctx.send("Nie udało się wygenerować obrazka. Spróbuj ponownie za chwilę.")
            return
        self.bot.log.error(error)

    @commands.command(description="Wpisz aby otrzymać losowe zdjęcie pieska", aliases=["pies", "piesek"])
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://dog.ceo/api/breeds/image/random') as r:
                if r.status == 200:
                    data = await r.json()
                    await ctx.send(data['message'])
                else:
                    raise commands.CommandError

    @dog.error
    async def dog_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("Nie udało się uzyskać obrazka. Spróbuj ponownie za chwilę.")
            return

    @commands.command(description="Rzut monetą", aliases=["moneta"])
    async def flip(self, ctx):
        embed = self.bot.embed(ctx.author)
        embed.title = "Rzut monetą"
        embed.description = "🪙 **{}**".format("Orzeł" if randrange(2) == 1 else "Reszka")
        await ctx.send(embed=embed)
