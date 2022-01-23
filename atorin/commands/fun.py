import textwrap
import unicodedata
from io import BytesIO
from random import randrange

import aiohttp
import discord
from discord.commands import Option, slash_command
import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from pyfiglet import Figlet
from bs4 import BeautifulSoup

from atorin.bot import Atorin
from ..config import config


class Fun(commands.Cog, name="🎲 Zabawa"):
    def __init__(self, bot: Atorin):
        self.bot = bot

    @slash_command(
        description="Losowe zdjęcie Shiba Inu", guild_ids=config["guild_ids"]
    )
    async def shiba(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get("http://shibe.online/api/shibes?count=1") as r:
                if r.status == 200:
                    data = await r.json()
                    embed = discord.Embed()
                    embed.title = "Losowe zdjęcie Shiba Inu"
                    embed.set_image(url=data[0])
                    await ctx.send_followup(embed=embed)
                else:
                    raise commands.CommandError(await r.text())

    @slash_command(
        description="Stwórz pasek z Wiadomości z własnym tekstem",
        guild_ids=config["guild_ids"],
    )
    async def tvp(
        self, ctx: discord.ApplicationContext, text: Option(str, "Treść paska")
    ):
        if len(text) > 48:
            raise commands.BadArgument(
                f"Treść paska jest zbyt długa! Max. 48 znaków, podano {len(text)}."
            )
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://pasek-tvpis.pl/index.php",
                data={"fimg": randrange(2), "msg": text},
            ) as r:
                if r.status == 200:
                    image = await r.content.read()
                    embed = discord.Embed()
                    embed.title = "Twój pasek z Wiadomości"
                    embed.set_image(url="attachment://tvp.png")
                    await ctx.send_followup(
                        embed=embed,
                        file=discord.File(BytesIO(image), filename="tvp.png"),
                    )
                else:
                    raise commands.CommandError(await r.text())

    @slash_command(
        description="Losowe zdjęcie kota",
        guild_ids=config["guild_ids"],
    )
    async def cat(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.thecatapi.com/v1/images/search?limit=1"
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    embed = discord.Embed()
                    embed.title = "Losowe zdjęcie kota"
                    embed.set_image(url=data[0]["url"])
                    await ctx.send_followup(embed=embed)
                else:
                    raise commands.CommandError(await r.text())

    @slash_command(description="Losowe zdjęcie lisa", guild_ids=config["guild_ids"])
    async def fox(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://randomfox.ca/floof/") as r:
                if r.status == 200:
                    data = await r.json()
                    embed = discord.Embed()
                    embed.title = "Losowe zdjęcie lisa"
                    embed.set_image(url=data["image"])
                    await ctx.send_followup(embed=embed)
                else:
                    raise commands.CommandError(await r.text())

    @slash_command(
        description="Wysyła napis stworzony z mniejszych znaków.",
        guild_ids=config["guild_ids"],
    )
    async def figlet(
        self, ctx: discord.ApplicationContext, text: Option(str, "Treść figletu")
    ):
        await ctx.defer()
        f = Figlet()
        figlet = f.renderText(text)
        if len(figlet) > 1990:
            raise commands.BadArgument(
                "Wygenerowany figlet jest za długi. Wybierz inny tekst i spróbuj ponownie."
            )
        embed = discord.Embed()
        embed.title = "Figlet"
        embed.description = f"```{figlet}```"
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Losowy commit",
        guild_ids=config["guild_ids"],
    )
    async def commit(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get("http://whatthecommit.com/index.txt") as r:
                if r.status == 200:
                    text = await r.text()
                    text = text.replace("\n", "")
                    embed = discord.Embed()
                    embed.title = "Losowy commit"
                    embed.description = f"`git commit -m '{text}'`"
                    await ctx.send_followup(embed=embed)
                else:
                    raise commands.CommandError(await r.text())

    @slash_command(
        description="Stwórz osiągnięcie z Minecrafta", guild_ids=config["guild_ids"]
    )
    async def achievement(
        self, ctx: discord.ApplicationContext, text: Option(str, "Treść osiągnięcia")
    ):
        if len(text) > 25:
            raise commands.BadArgument(
                f"Treść osiągnięcia jest zbyt długa! Max. 25 znaków, podano {len(text)}."
            )
        await ctx.defer()
        text = (
            unicodedata.normalize("NFKD", text)
            .replace("ł", "l")
            .replace("Ł", "L")
            .encode("ASCII", "ignore")
            .decode("UTF-8")
        )
        template = Image.open("assets/achievement/{0}.png".format(randrange(1, 39)))
        d1 = ImageDraw.Draw(template)
        font = ImageFont.truetype("assets/achievement/font.ttf", 16)
        d1.text((60, 7), "Osiagniecie zdobyte!", font=font, fill=(255, 255, 0))
        d1.text((60, 30), text, font=font)
        img = BytesIO()
        template.save(img, "PNG")
        img.seek(0)
        embed = discord.Embed()
        embed.title = "Twoje Minecraftowe osiągnięcie"
        embed.set_image(url="attachment://achievement.png")
        await ctx.send_followup(
            embed=embed, file=discord.File(img, filename="achievement.png")
        )

    @slash_command(
        description="Stwórz własnego mema z Drake", guild_ids=config["guild_ids"]
    )
    async def drake(
        self,
        ctx: discord.ApplicationContext,
        upper_text: Option(str, "Tekst górny"),
        bottom_text: Option(str, "Tekst dolny"),
    ):
        lines = [upper_text, bottom_text]
        await ctx.defer()
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
        embed = discord.Embed()
        embed.title = "Twój mem z Drake"
        embed.set_image(url="attachment://drake.png")
        await ctx.send_followup(
            embed=embed, file=discord.File(img, filename="drake.png")
        )

    @slash_command(
        description="Stwórz kod QR z tekstem lub linkiem",
        guild_ids=config["guild_ids"],
    )
    async def codeqr(
        self, ctx: discord.ApplicationContext, content: Option(str, "Treść kodu QR")
    ):
        await ctx.defer()
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(content)
        qr.make(fit=True)
        code = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        logo = Image.open("assets/qrcode/logo.png")
        logo.thumbnail((60, 60))
        logo_pos = (
            (code.size[0] - logo.size[0]) // 2,
            (code.size[1] - logo.size[1]) // 2,
        )
        code.paste(logo, logo_pos)
        img = BytesIO()
        code.save(img, "PNG")
        img.seek(0)
        embed = discord.Embed()
        embed.title = "Twój kod QR"
        embed.set_image(url="attachment://qr.png")
        await ctx.send_followup(file=discord.File(img, filename="qr.png"))

    # @slash_command(
    #     description="Pokazuje profil z Instagrama", guild_ids=config["guild_ids"]
    # )
    # async def instagram(
    #     self, ctx, name: Option(str, "Nazwa użytkownika na Instagramie")
    # ):
    #     await ctx.defer()
    #     cookies = []
    #     for cookie in self.bot.config["instagram"]:
    #         cookies.append(cookie["name"] + "=" + cookie["value"])
    #     name = name.replace("@", "")
    #     r = requests.get(
    #         f"https://www.instagram.com/{name}/?__a=1",
    #         headers={"cookie": "; ".join(cookies)},
    #     )
    #     if r.status_code == 404:
    #         raise commands.BadArgument("Nie znaleziono użytkownika o takiej nazwie!")
    #     data = r.json()
    #     if "graphql" not in data:
    #         raise commands.CommandError(r.text)
    #     embed = discord.Embed()
    #     user = data["graphql"]["user"]
    #     embed.title = "Profil {} na Instagramie".format(user["username"])
    #     if user["full_name"]:
    #         embed.add_field(name="😊 Pełna nazwa", value=user["full_name"], inline=False)
    #     if not user["is_private"]:
    #         embed.add_field(name="🔑 Prywatne", value="Nie")
    #     else:
    #         embed.add_field(name="🔑 Prywatne", value="Tak")
    #     if user["biography"]:
    #         embed.add_field(
    #             name="📝 Opis",
    #             value=f"```yml\n{user['biography']}```",
    #             inline=False,
    #         )
    #     embed.add_field(
    #         name="😍 Obserwujących", value=str(user["edge_followed_by"]["count"])
    #     )
    #     embed.add_field(name="👀 Obserwuje", value=str(user["edge_follow"]["count"]))
    #     embed.add_field(
    #         name="🔗 Link",
    #         value=f"https://instagram.com/{user['username']}",
    #         inline=False,
    #     )
    #     if user["profile_pic_url_hd"]:
    #         embed.set_thumbnail(url=user["profile_pic_url_hd"])
    #     await ctx.send_followup(embed=embed)

    @slash_command(
        description="Tworzy plakat WANTED z wybraną osobą",
        guild_ids=config["guild_ids"],
    )
    async def wanted(
        self,
        ctx: discord.ApplicationContext,
        user: Option(discord.Member, "Osoba poszukiwana"),
    ):
        await ctx.defer()
        template = Image.open("assets/wanted/wanted.jpg")
        avatar = Image.open(BytesIO(await user.display_avatar.read()))
        avatar_resized = avatar.resize((320, 320))
        w, h = avatar_resized.size
        template.paste(avatar_resized, (44, 123, 44 + w, 123 + h))
        img = BytesIO()
        template.save(img, "PNG")
        img.seek(0)
        embed = discord.Embed()
        embed.title = f"Twój plakat WANTED z {user}"
        embed.set_image(url="attachment://wanted.png")
        await ctx.send_followup(
            embed=embed, file=discord.File(img, filename="wanted.png")
        )

    @slash_command(description="Losowe zdjęcie psa", guild_ids=config["guild_ids"])
    async def dog(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dog.ceo/api/breeds/image/random") as r:
                if r.status == 200:
                    data = await r.json()
                    embed = discord.Embed()
                    embed.title = "Losowe zdjęcie psa"
                    embed.set_image(url=data["message"])
                    await ctx.send_followup(embed=embed)
                else:
                    raise commands.CommandError(await r.text())

    @slash_command(description="Rzut monetą", guild_ids=config["guild_ids"])
    async def flip(self, ctx: discord.ApplicationContext):
        embed = discord.Embed()
        embed.title = "Rzut monetą"
        embed.description = f"🪙 **{'Orzeł' if randrange(2) == 1 else 'Reszka'}**"
        await ctx.respond(embed=embed)

    @slash_command(
        description="Generuje mema Change my mind", guild_ids=config["guild_ids"]
    )
    async def changemymind(
        self, ctx: discord.ApplicationContext, text: Option(str, "Treść mema")
    ):
        if len(text) > 140:
            raise commands.BadArgument(
                f"Treść mema jest zbyt długa! Max. 140 znaków, podano {len(text)}"
            )
        await ctx.defer()
        template = Image.open("assets/changemymind/changemymind.jpg")
        txt = Image.new("RGBA", (700, 350), (0, 0, 0, 0))
        d1 = ImageDraw.Draw(txt)
        font = ImageFont.truetype("assets/changemymind/impact.ttf", 24)
        offset = 0
        for line in textwrap.wrap(text.strip(), width=30):
            d1.text((50, offset), line, font=font, fill="#000000")
            offset += font.getsize(line)[1]
        w = txt.rotate(22.5)
        template.paste(w, (310, 200), w)
        img = BytesIO()
        template.save(img, "PNG")
        img.seek(0)
        embed = discord.Embed()
        embed.title = "Change my mind"
        embed.set_image(url="attachment://changemymind.png")
        await ctx.send_followup(
            embed=embed, file=discord.File(img, filename="changemymind.png")
        )

    @slash_command(
        description="Wysyła losowego mema z /r/Polska_wpz",
        guild_ids=config["guild_ids"],
    )
    async def meme(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        while True:
            r = requests.get(
                "https://reddit.com/r/Polska_wpz/random/.json",
                headers={"User-agent": "Atorin"},
            )
            meme = r.json()[0]["data"]["children"][0]["data"]
            if meme["url"].endswith(".jpg") or meme["url"].endswith(".png"):
                break
        embed = discord.Embed()
        embed.title = (
            (meme["title"][:200] + "...") if len(meme["title"]) > 203 else meme["title"]
        )
        embed.set_image(url=meme["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(description="Losowy słodki obrazek", guild_ids=config["guild_ids"])
    async def aww(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        while True:
            r = requests.get(
                "https://reddit.com/r/aww/random/.json",
                headers={"User-agent": "Atorin"},
            )
            post = r.json()[0]["data"]["children"][0]["data"]
            if post["url"].endswith(".jpg") or post["url"].endswith(".png"):
                break
        embed = discord.Embed()
        embed.title = (
            (post["title"][:200] + "...") if len(post["title"]) > 203 else post["title"]
        )
        embed.set_image(url=post["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(description="Losowe zdjęcie żółwia", guild_ids=config["guild_ids"])
    async def turtle(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        while True:
            r = requests.get(
                "https://reddit.com/r/turtle/random/.json",
                headers={"User-agent": "Atorin"},
            )
            post = r.json()[0]["data"]["children"][0]["data"]
            if post["url"].endswith(".jpg") or post["url"].endswith(".png"):
                break
        embed = discord.Embed()
        embed.title = (
            (post["title"][:200] + "...") if len(post["title"]) > 203 else post["title"]
        )
        embed.set_image(url=post["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(description="Losowe zdjęcie alpaki", guild_ids=config["guild_ids"])
    async def alpaca(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        while True:
            r = requests.get(
                "https://reddit.com/r/alpaca/random/.json",
                headers={"User-agent": "Atorin"},
            )
            post = r.json()[0]["data"]["children"][0]["data"]
            if post["url"].endswith(".jpg") or post["url"].endswith(".png"):
                break
        embed = discord.Embed()
        embed.title = (
            (post["title"][:200] + "...") if len(post["title"]) > 203 else post["title"]
        )
        embed.set_image(url=post["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(description="Losowe zdjęcie żaby", guild_ids=config["guild_ids"])
    async def frog(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        while True:
            r = requests.get(
                "https://reddit.com/r/frogs/random/.json",
                headers={"User-agent": "Atorin"},
            )
            post = r.json()[0]["data"]["children"][0]["data"]
            if post["url"].endswith(".jpg") or post["url"].endswith(".png"):
                break
        embed = discord.Embed()
        embed.title = (
            (post["title"][:200] + "...") if len(post["title"]) > 203 else post["title"]
        )
        embed.set_image(url=post["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Astronomiczne zdjęcie dnia", guild_ids=config["guild_ids"]
    )
    async def apod(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        r = requests.get(
            "https://apod.nasa.gov/apod/", headers={"User-agent": "Atorin"}
        )
        soup = BeautifulSoup(r.content, "html.parser")
        soup.find_all("p")[2].p.clear()
        if r.status_code != 200:
            raise commands.CommandError(r.text)
        embed = discord.Embed()
        embed.title = "Astronomiczne zdjęcie dnia"
        embed.set_image(url=f"{r.url}{soup.find_all('p')[0].img['src']}")
        embed.description = f"**{soup.find_all('b')[0].text.strip()}**"
        embed.url = r.url
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Wysyła podaną wiadomość jako Atorin",
        guild_ids=config["guild_ids"],
    )
    async def say(
        self, ctx: discord.ApplicationContext, content: Option(str, "Treść wiadomości")
    ):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.respond(content)


def setup(bot):
    bot.add_cog(Fun(bot))
