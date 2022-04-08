import textwrap
import unicodedata
from io import BytesIO
from random import randint

import discord
from discord.commands import Option, slash_command
import qrcode
import httpx
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
        description="Random photo of Shiba Inu",
        description_localizations={"pl": "Losowe zdjęcie Shiba Inu"},
        guild_ids=config["guild_ids"],
    )
    async def shiba(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get("http://shibe.online/api/shibes?count=1")
        if r.status_code == 200:
            data = r.json()
            embed = discord.Embed()
            embed.title = "Losowe zdjęcie Shiba Inu" if ctx.interaction.locale == "pl" else "Random photo of Shiba Inu"
            embed.set_image(url=data[0])
            await ctx.send_followup(embed=embed)
        else:
            raise commands.CommandError(
                f"Wystąpił błąd przy pobieraniu zdjęcia, spróbuj ponownie później. [{r.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while downloading photo, try again later. [{r.status_code}]"
            )

    @slash_command(
        description="Generate headline from Polish TV news program",
        description_localizations={"pl": "Stwórz pasek z Wiadomości z własnym tekstem"},
        guild_ids=config["guild_ids"],
    )
    async def tvp(
        self,
        ctx: discord.ApplicationContext,
        text: Option(
            str,
            name="text",
            name_localizations={"pl": "tekst"},
            description="Type content of headline",
            description_localizations={"pl": "Wpisz treść paska"},
        ),
    ):
        if len(text) > 48:
            raise commands.BadArgument(
                f"Treść paska jest zbyt długa! Max. 48 znaków, podano {len(text)}."
                if ctx.interaction.locale == "pl"
                else f"Your text is too long! Max. 48 characters, given {len(text)}."
            )
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://pasek-tvpis.pl/index.php",
                data={"fimg": randint(0, 1), "msg": text},
                follow_redirects=True,
            )
        if r.status_code == 200:
            image = r.content
            embed = discord.Embed()
            embed.title = (
                "Twój pasek z Wiadomości" if ctx.interaction.locale == "pl" else "Your headline from Polish TV news"
            )
            embed.set_image(url="attachment://tvp.png")
            await ctx.send_followup(
                embed=embed,
                file=discord.File(BytesIO(image), filename="tvp.png"),
            )
        else:
            raise commands.CommandError(
                f"Wystąpił błąd przy pobieraniu obrazka, spróbuj ponownie później. [{r.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while downloading image, try again later. [{r.status_code}]"
            )

    @slash_command(
        description="Random photo of cat",
        description_localizations={"pl": "Losowe zdjęcie kota"},
        guild_ids=config["guild_ids"],
    )
    async def cat(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.thecatapi.com/v1/images/search?limit=1")
        if r.status_code == 200:
            data = r.json()
            embed = discord.Embed()
            embed.title = "Losowe zdjęcie kota" if ctx.interaction.locale == "pl" else "Random photo of cat"
            embed.set_image(url=data[0]["url"])
            await ctx.send_followup(embed=embed)
        else:
            raise commands.CommandError(
                f"Wystąpił błąd przy pobieraniu zdjęcia, spróbuj ponownie później. [{r.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while downloading photo, try again later. [{r.status_code}]"
            )

    @slash_command(
        description="Random photo of fox",
        description_localizations={"pl": "Losowe zdjęcie lisa"},
        guild_ids=config["guild_ids"],
    )
    async def fox(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get("https://randomfox.ca/floof/")
        if r.status_code == 200:
            data = r.json()
            embed = discord.Embed()
            embed.title = "Losowe zdjęcie lisa" if ctx.interaction.locale == "pl" else "Random photo of fox"
            embed.set_image(url=data["image"])
            await ctx.send_followup(embed=embed)
        else:
            raise commands.CommandError(
                f"Wystąpił błąd przy pobieraniu zdjęcia, spróbuj ponownie później. [{r.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while downloading photo, try again later. [{r.status_code}]"
            )

    @slash_command(
        description="Creates ASCII art from text",
        description_localizations={"pl": "Wysyła napis stworzony z mniejszych znaków"},
        guild_ids=config["guild_ids"],
    )
    async def figlet(
        self,
        ctx: discord.ApplicationContext,
        text: Option(
            str,
            name="text",
            name_localizations={"pl": "tekst"},
            description="Type content of figlet",
            description_localizations={"pl": "Wpisz treść figletu"},
        ),
    ):
        await ctx.defer()
        f = Figlet()
        figlet = f.renderText(text)
        if len(figlet) > 1990:
            raise commands.BadArgument(
                "Wygenerowany figlet jest za długi. Wybierz inny tekst i spróbuj ponownie."
                if ctx.interaction.locale == "pl"
                else "Generated figlet is too long. Choose shorter text and try again."
            )
        embed = discord.Embed()
        embed.title = "Figlet"
        embed.description = f"```{figlet}```"
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Random commit title",
        description_localizations={"pl": "Losowy commit"},
        guild_ids=config["guild_ids"],
    )
    async def commit(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get("http://whatthecommit.com/index.txt")
        if r.status_code == 200:
            text = r.text.replace("\n", "")
            embed = discord.Embed()
            embed.title = "Losowy commit" if ctx.interaction.locale == "pl" else "Random commit"
            embed.description = f"`git commit -m '{text}'`"
            await ctx.send_followup(embed=embed)
        else:
            raise commands.CommandError(
                f"Wystąpił błąd przy pobieraniu commita, spróbuj ponownie później. [{r.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while downloading commit, try again later. [{r.status_code}]"
            )

    @slash_command(
        description="Create achievement from Minecraft",
        description_localizations={"pl": "Stwórz osiągnięcie z Minecrafta"},
        guild_ids=config["guild_ids"],
    )
    async def achievement(
        self,
        ctx: discord.ApplicationContext,
        text: Option(
            str,
            name="text",
            name_localizations={"pl": "tekst"},
            description="Type content of achievement",
            description_localizations={"pl": "Wpisz treść osiągnięcia"},
        ),
    ):
        if len(text) > 25:
            raise commands.BadArgument(
                f"Treść osiągnięcia jest zbyt długa! Max. 25 znaków, podano {len(text)}."
                if ctx.interaction.locale == "pl"
                else f"Your text is too long! Max. 25 characters, given {len(text)}."
            )
        await ctx.defer()
        text = (
            unicodedata.normalize("NFKD", text)
            .replace("ł", "l")
            .replace("Ł", "L")
            .encode("ASCII", "ignore")
            .decode("UTF-8")
        )
        template = Image.open("assets/achievement/{0}.png".format(randint(1, 39)))
        d1 = ImageDraw.Draw(template)
        font = ImageFont.truetype("assets/achievement/font.ttf", 16)
        d1.text(
            (60, 7),
            "Osiagniecie zdobyte!" if ctx.interaction.locale == "pl" else "Achievement get!",
            font=font,
            fill=(255, 255, 0),
        )
        d1.text((60, 30), text, font=font)
        img = BytesIO()
        template.save(img, "PNG")
        img.seek(0)
        embed = discord.Embed()
        embed.title = (
            "Twoje Minecraftowe osiągnięcie" if ctx.interaction.locale == "pl" else "Your Minecraft achievement"
        )
        embed.set_image(url="attachment://achievement.png")
        await ctx.send_followup(embed=embed, file=discord.File(img, filename="achievement.png"))

    @slash_command(
        description="Create Drake meme",
        description_localizations={"pl": "Stwórz własnego mema z Drake"},
        guild_ids=config["guild_ids"],
    )
    async def drake(
        self,
        ctx: discord.ApplicationContext,
        upper_text: Option(
            str,
            name="upper_text",
            name_localizations={"pl": "tekst_górny"},
            description="Upper text",
            description_localizations={"pl": "Tekst górny"},
        ),
        bottom_text: Option(
            str,
            name="bottom_text",
            name_localizations={"pl": "tekst_dolny"},
            description="Bottom text",
            description_localizations={"pl": "Tekst dolny"},
        ),
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
        embed.title = "Twój mem z Drake" if ctx.interaction.locale == "pl" else "Your Drake meme"
        embed.set_image(url="attachment://drake.png")
        await ctx.send_followup(embed=embed, file=discord.File(img, filename="drake.png"))

    @slash_command(
        description="Create QR Code",
        description_localizations={"pl": "Stwórz kod QR z tekstem lub linkiem"},
        guild_ids=config["guild_ids"],
    )
    async def codeqr(
        self,
        ctx: discord.ApplicationContext,
        content: Option(
            str,
            name="content",
            name_localizations={"pl": "zawartość"},
            description="Enter data",
            description_localizations={"pl": "Wpisz zawartość kodu QR"},
        ),
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
        embed.title = "Twój kod QR" if ctx.interaction.locale == "pl" else "Your QR code"
        embed.set_image(url="attachment://qr.png")
        await ctx.send_followup(file=discord.File(img, filename="qr.png"))

    @slash_command(
        description="Create WANTED poster with selected person",
        description_localizations={"pl": "Tworzy plakat WANTED z wybraną osobą"},
        guild_ids=config["guild_ids"],
    )
    async def wanted(
        self,
        ctx: discord.ApplicationContext,
        user: Option(
            discord.Member,
            name="user",
            name_localizations={"pl": "osoba"},
            description="Select person to be wanted",
            description_localizations={"pl": "Wybierz osobę, która ma być poszukiwana"},
        ),
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
        embed.title = (
            f"Twój plakat WANTED z {user}" if ctx.interaction.locale == "pl" else f"Your WANTED poster with {user}"
        )
        embed.set_image(url="attachment://wanted.png")
        await ctx.send_followup(embed=embed, file=discord.File(img, filename="wanted.png"))

    @slash_command(
        description="Random photo of dog",
        description_localizations={"pl": "Losowe zdjęcie psa"},
        guild_ids=config["guild_ids"],
    )
    async def dog(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get("https://dog.ceo/api/breeds/image/random")
        if r.status_code == 200:
            data = r.json()
            embed = discord.Embed()
            embed.title = "Losowe zdjęcie psa" if ctx.interaction.locale == "pl" else "Random photo of dog"
            embed.set_image(url=data["message"])
            await ctx.send_followup(embed=embed)
        else:
            raise commands.CommandError(
                f"Wystąpił błąd przy pobieraniu zdjęcia, spróbuj ponownie później. [{r.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while downloading photo, try again later. [{r.status_code}]"
            )

    @slash_command(
        description="Coin flip", description_localizations={"pl": "Rzut monetą"}, guild_ids=config["guild_ids"]
    )
    async def flip(self, ctx: discord.ApplicationContext):
        embed = discord.Embed()
        embed.title = "Rzut monetą" if ctx.interaction.locale == "pl" else "Coin flip"
        if ctx.interaction.locale == "pl":
            embed.description = f"🪙 **{'Orzeł' if randint(0, 1) == 1 else 'Reszka'}**"
        else:
            embed.description = f"🪙 **{'Heads' if randint(0, 1) == 1 else 'Tails'}**"
        await ctx.respond(embed=embed)

    @slash_command(
        description="Create Change my mind meme",
        description_localizations={"pl": "Generuje mema Change my mind"},
        guild_ids=config["guild_ids"],
    )
    async def changemymind(
        self,
        ctx: discord.ApplicationContext,
        text: Option(
            str,
            name="text",
            name_localizations={"pl": "tekst"},
            description="Type content of meme",
            description_localizations={"pl": "Wpisz treść mema"},
        ),
    ):
        if len(text) > 140:
            raise commands.BadArgument(
                f"Treść mema jest zbyt długa! Max. 140 znaków, podano {len(text)}"
                if ctx.interaction.locale == "pl"
                else f"Your text is too long! Max. 140 characters, given {len(text)}"
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
        await ctx.send_followup(embed=embed, file=discord.File(img, filename="changemymind.png"))

    @slash_command(
        description="Random meme from r/Polska_wpz",
        description_localizations={"pl": "Wysyła losowego mema z /r/Polska_wpz"},
        guild_ids=config["guild_ids"],
    )
    async def meme(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            while True:
                r = await client.get(
                    "https://reddit.com/r/Polska_wpz/random/.json",
                    headers={"User-agent": "Atorin"},
                    follow_redirects=True,
                )
                meme = r.json()[0]["data"]["children"][0]["data"]
                if meme["url"].endswith(".jpg") or meme["url"].endswith(".png"):
                    break
        embed = discord.Embed()
        embed.title = (meme["title"][:200] + "...") if len(meme["title"]) > 203 else meme["title"]
        embed.set_image(url=meme["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Random cute picture",
        description_localizations={"pl": "Losowy słodki obrazek"},
        guild_ids=config["guild_ids"],
    )
    async def aww(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            while True:
                r = await client.get(
                    "https://reddit.com/r/aww/random/.json",
                    headers={"User-agent": "Atorin"},
                    follow_redirects=True,
                )
                post = r.json()[0]["data"]["children"][0]["data"]
                if post["url"].endswith(".jpg") or post["url"].endswith(".png"):
                    break
        embed = discord.Embed()
        embed.title = (post["title"][:200] + "...") if len(post["title"]) > 203 else post["title"]
        embed.set_image(url=post["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Random photo of turtle",
        description_localizations={"pl": "Losowe zdjęcie żółwia"},
        guild_ids=config["guild_ids"],
    )
    async def turtle(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            while True:
                r = await client.get(
                    "https://reddit.com/r/turtle/random/.json",
                    headers={"User-agent": "Atorin"},
                    follow_redirects=True,
                )
                post = r.json()[0]["data"]["children"][0]["data"]
                if post["url"].endswith(".jpg") or post["url"].endswith(".png"):
                    break
        embed = discord.Embed()
        embed.title = (post["title"][:200] + "...") if len(post["title"]) > 203 else post["title"]
        embed.set_image(url=post["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Random photo of alpaca",
        description_localizations={"pl": "Losowe zdjęcie alpaki"},
        guild_ids=config["guild_ids"],
    )
    async def alpaca(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            while True:
                r = await client.get(
                    "https://reddit.com/r/alpaca/random/.json",
                    headers={"User-agent": "Atorin"},
                    follow_redirects=True,
                )
                post = r.json()[0]["data"]["children"][0]["data"]
                if post["url"].endswith(".jpg") or post["url"].endswith(".png"):
                    break
        embed = discord.Embed()
        embed.title = (post["title"][:200] + "...") if len(post["title"]) > 203 else post["title"]
        embed.set_image(url=post["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Random photo of frog",
        description_localizations={"pl": "Losowe zdjęcie żaby"},
        guild_ids=config["guild_ids"],
    )
    async def frog(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            while True:
                r = await client.get(
                    "https://reddit.com/r/frogs/random/.json",
                    headers={"User-agent": "Atorin"},
                    follow_redirects=True,
                )
                post = r.json()[0]["data"]["children"][0]["data"]
                if post["url"].endswith(".jpg") or post["url"].endswith(".png"):
                    break
        embed = discord.Embed()
        embed.title = (post["title"][:200] + "...") if len(post["title"]) > 203 else post["title"]
        embed.set_image(url=post["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(
        ddescription="Astronomy Picture of the Day",
        description_localizations={"pl": "Astronomiczne zdjęcie dnia"},
        guild_ids=config["guild_ids"],
    )
    async def apod(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get("https://apod.nasa.gov/apod/", headers={"User-agent": "Atorin"})
        soup = BeautifulSoup(r.content, "html.parser")
        soup.find_all("p")[2].p.clear()
        if r.status_code != 200:
            raise commands.CommandError(
                f"Wystąpił błąd przy pobieraniu zdjęcia, spróbuj ponownie później. [{r.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while downloading photo, try again later. [{r.status_code}]"
            )
        embed = discord.Embed()
        embed.title = (
            "Astronomiczne zdjęcie dnia" if ctx.interaction.locale == "pl" else "Astronomy Picture of the Day"
        )
        embed.description = f"**{soup.find_all('b')[0].text.strip()}**"
        try:
            embed.set_image(url=f"{r.url}{soup.find_all('p')[0].img['src']}")
        except TypeError:
            embed.description += f"\n{soup.find_all('p')[0].iframe['src'].replace('/embed/', '/watch/')}"
        embed.url = str(r.url)
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Random photo of pigeon",
        description_localizations={"pl": "Losowe zdjęcie gołębia"},
        guild_ids=config["guild_ids"],
    )
    async def pigeon(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            while True:
                r = await client.get(
                    "https://reddit.com/r/pigeon/random/.json",
                    headers={"User-agent": "Atorin"},
                    follow_redirects=True,
                )
                post = r.json()[0]["data"]["children"][0]["data"]
                if post["url"].endswith(".jpg") or post["url"].endswith(".png"):
                    break
        embed = discord.Embed()
        embed.title = (post["title"][:200] + "...") if len(post["title"]) > 203 else post["title"]
        embed.set_image(url=post["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Random photo of duck",
        description_localizations={"pl": "Losowe zdjęcie kaczki"},
        guild_ids=config["guild_ids"],
    )
    async def duck(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            while True:
                r = await client.get(
                    "https://reddit.com/r/duck/random/.json",
                    headers={"User-agent": "Atorin"},
                    follow_redirects=True,
                )
                post = r.json()[0]["data"]["children"][0]["data"]
                if post["url"].endswith(".jpg") or post["url"].endswith(".png"):
                    break
        embed = discord.Embed()
        embed.title = (post["title"][:200] + "...") if len(post["title"]) > 203 else post["title"]
        embed.set_image(url=post["url"])
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Random comic from xkcd.com",
        description_localizations={"pl": "Losowy komiks z xkcd.com"},
        guild_ids=config["guild_ids"],
    )
    async def xkcd(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            latest = await client.get(
                f"https://xkcd.com/info.0.json",
                headers={"User-agent": "Atorin"},
            )
        if not latest.status_code == 200:
            raise commands.CommandError(
                f"Wystąpił błąd przy pobieraniu komiksu, spróbuj ponownie później. [{latest.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while downloading comic, try again later. [{latest.status_code}]"
            )
        latest_number = latest.json()["num"]
        random_comic = randint(1, latest_number)
        async with httpx.AsyncClient() as client:
            comic = await client.get(
                url=f"https://xkcd.com/{random_comic}/info.0.json",
                headers={"User-agent": "Atorin"},
            )
        if not comic.status_code == 200:
            raise commands.CommandError(
                f"Wystąpił błąd przy pobieraniu komiksu, spróbuj ponownie później. [{comic.status_code}]"
                if ctx.interaction.locale == "pl"
                else f"Error has occurred while downloading comic, try again later. [{comic.status_code}]"
            )
        comic_data = comic.json()
        embed = discord.Embed()
        embed.title = comic_data["title"]
        embed.set_image(url=comic_data["img"])
        await ctx.send_followup(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
