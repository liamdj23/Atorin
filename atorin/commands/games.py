"""
```yml
    _   _             _       
   / \ | |_ ___  _ __(_)_ __  
  / _ \| __/ _ \| '__| | '_ \ 
 / ___ \ || (_) | |  | | | | |
/_/   \_\__\___/|_|  |_|_| |_|
```
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                              
Made with ❤️ by Piotr Gaździcki.

"""
import re
from io import BytesIO
from urllib.parse import quote, urlparse
from discord.commands.commands import OptionChoice
import humanize
import requests

import aiohttp
import discord
from discord.ext import commands
from discord.commands import slash_command, Option

from atorin.bot import Atorin
from ..config import config


def is_domain(argument: str):
    regex = "^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}"
    p = re.compile(regex)
    if re.search(p, argument):
        return argument
    raise commands.BadArgument


def is_minecraft_nick(argument: str):
    regex = r"^\w{3,16}$"
    p = re.compile(regex)
    if re.search(p, argument):
        return argument
    raise commands.BadArgument


def is_platform(argument: str):
    if argument.lower() in ["epic", "psn", "xbl"]:
        return argument.lower()
    raise commands.BadArgument


async def steam_resolve_url(url: str, key: str):
    parsed = urlparse(url)
    if not parsed.netloc:
        parsed = urlparse("https://" + url)
    nick = parsed.path.split("/")[2]
    try:
        int(nick)
        return nick, nick
    except ValueError:
        pass
    async with aiohttp.ClientSession() as session:
        api = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v1?vanityurl={0}&key={1}".format(
            quote(nick), key
        )
        async with session.get(api) as r:
            if r.status == 200:
                data = await r.json()
                if "steamid" not in data["response"]:
                    return None
                return data["response"]["steamid"], nick


async def steam_get_stats(app_id: int, key: str, steam_id: int):
    async with aiohttp.ClientSession() as session:
        api = "http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={0}&key={1}&steamid={2}".format(
            app_id, key, steam_id
        )
        async with session.get(api) as r:
            if r.status == 200:
                data = await r.json()
                if "playerstats" in data and "stats" in data["playerstats"]:
                    return data["playerstats"]["stats"]


class Games(commands.Cog, name="🕹 Gry"):
    def __init__(self, bot: Atorin):
        self.bot = bot

    @slash_command(
        description="Status serwera Minecraft", guild_ids=[408960275933429760]
    )
    async def mcsrv(
        self, ctx: discord.ApplicationContext, domain: Option(str, "Adres serwera")
    ):
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.mcsrvstat.us/2/{domain}") as r:
                r.raise_for_status()
                data = await r.json()
                if not data["online"]:
                    async with session.get(
                        f"https://api.mcsrvstat.us/bedrock/2/{domain}"
                    ) as r:
                        r.raise_for_status()
                        data = await r.json()
                        if not data["online"]:
                            raise commands.BadArgument(
                                "Adres serwera jest niepoprawny lub serwer jest offline!"
                            )
                embed = discord.Embed()
                embed.title = f"Status serwera Minecraft: {domain}"
                if "version" in data:
                    embed.add_field(name="⚙️ Wersja", value=data["version"])
                if "players" in data:
                    embed.add_field(
                        name="👥 Liczba graczy",
                        value=f"{data['players']['online']}/{data['players']['max']}",
                    )
                if "software" in data:
                    embed.add_field(
                        name="🗜 Silnik",
                        value=f"`{data['software']}`",
                        inline=False,
                    )
                if "plugins" in data:
                    embed.add_field(
                        name="🔌 Pluginy",
                        value=f"`{', '.join(data['plugins']['names'])}`",
                        inline=False,
                    )
                if "motd" in data:
                    embed.add_field(
                        name="🔠 MOTD",
                        value="```yml\n"
                        + "\n".join(data["motd"]["clean"]).strip()
                        + "\n```",
                        inline=False,
                    )
                embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{domain}")
                await ctx.send_followup(embed=embed)

    @slash_command(
        description="Wyświetla Twojego skina w Minecraft",
        guild_ids=[408960275933429760],
    )
    async def mcskin(
        self, ctx: discord.ApplicationContext, nick: Option(str, "Nick w Minecraft")
    ):
        await ctx.defer()
        mojang = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{nick}")
        if mojang.status_code == 200:
            data = mojang.json()
            skin = requests.get(f"https://crafatar.com/renders/body/{data['id']}")
            if skin.status_code == 200:
                embed = discord.Embed()
                embed.title = f"Skin {nick} w Minecraft"
                embed.set_image(url="attachment://skin.png")
                await ctx.send_followup(
                    embed=embed,
                    files=[discord.File(BytesIO(skin.content), filename="skin.png")],
                )
            else:
                raise commands.CommandError(skin.text)
        elif mojang.status_code == 204:
            raise commands.BadArgument("Podany gracz nie został odnaleziony!")
        else:
            raise commands.CommandError(mojang.text)

    @slash_command(
        description="Statystyki w grze Fortnite", guild_ids=[408960275933429760]
    )
    async def fortnite(
        self,
        ctx: discord.ApplicationContext,
        platform: Option(
            str,
            "Wybierz platformę na której grasz",
            choices=[
                OptionChoice("Epic Games", "epic"),
                OptionChoice("Playstation Network", "psn"),
                OptionChoice("Xbox Live", "xbl"),
            ],
        ),
        nick: Option(str, "Nick gracza"),
    ):
        await ctx.defer()
        r = requests.get(
            url="https://fortnite-api.com/v2/stats/br/v2",
            params={"name": nick, "accountType": platform},
            headers={"Authorization": config["fortnite"]},
        )
        if r.status_code == 200:
            json = r.json()
            data = json["data"]["stats"]["all"]["overall"]
            embed = discord.Embed()
            embed.title = "Statystyki w grze Fortnite"
            embed.description = "🧑 Gracz: **{}**".format(nick)
            embed.add_field(name="⭐️ Punkty", value=humanize.intcomma(data["score"]))
            embed.add_field(name="🏆 Wygrane", value=humanize.intcomma(data["wins"]))
            embed.add_field(name="⚔ Zabójstwa", value=humanize.intcomma(data["kills"]))
            embed.add_field(name="☠ Śmierci", value=humanize.intcomma(data["deaths"]))
            embed.add_field(
                name="🕹 Rozegranych meczy", value=humanize.intcomma(data["matches"])
            )
            await ctx.send_followup(embed=embed)
        elif r.status_code == 403:
            raise commands.BadArgument(f"Statystyki gracza __{nick}__ są **prywatne**!")
        elif r.status_code == 404:
            raise commands.BadArgument(
                "Podany gracz nie istnieje lub nigdy nie grał w Fortnite!"
            )
        else:
            raise commands.CommandError(await r.text())

    @slash_command(
        description="Statystyki w grze CS:GO", guild_ids=[408960275933429760]
    )
    async def csgo(
        self, ctx: discord.ApplicationContext, url: Option(str, "Link do profilu Steam")
    ):
        await ctx.defer()
        if "steamcommunity.com/id/" in url or "steamcommunity.com/profiles/" in url:
            try:
                steam_id, nick = await steam_resolve_url(url, config["steam"])
            except TypeError:
                raise commands.BadArgument("Nie odnaleziono podanego gracza!")
        else:
            raise commands.BadArgument("Podany link jest nieprawidłowy!")
        stats = await steam_get_stats(730, config["steam"], steam_id)
        if not stats:
            raise commands.BadArgument("Podany profil musi być publiczny!")
        embed = discord.Embed()
        embed.title = "Statystyki w grze CS:GO"
        embed.description = "🧑 Gracz: **{}**".format(nick)
        for i in stats:
            if i["name"] == "total_kills":
                embed.add_field(name="🔫 Liczba zabójstw", value=i["value"])
            elif i["name"] == "total_deaths":
                embed.add_field(name="☠ Liczba śmierci", value=i["value"])
            elif i["name"] == "total_matches_played":
                embed.add_field(name="⚔ Rozegranych meczy", value=i["value"])
            elif i["name"] == "total_matches_won":
                embed.add_field(
                    name="🏆 Wygranych meczy", value=i["value"], inline=False
                )
        await ctx.send_followup(embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))
