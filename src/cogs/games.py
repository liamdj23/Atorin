import base64
import re
from io import BytesIO
from urllib.parse import quote, urlparse
import requests

import aiohttp
import discord
from discord.ext import commands


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
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        aliases=["mc"],
        usage="<srv|skin> <adres|nick>",
        description="Wpisz aby otrzymać skina gracza lub sprawdzić status serwera Minecraft\n\n"
        + "Przykłady użycia:\n"
        + "&mc srv krainamc.pl\n"
        + "&mc skin liamdj23",
    )
    async def minecraft(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("❌ Poprawne użycie: `&mc <srv|skin> <adres|nick>`")

    @minecraft.command(aliases=["srv"])
    async def server(self, ctx, domain: is_domain):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.mcsrvstat.us/2/{domain}") as r:
                if r.status == 200:
                    data = await r.json()
                    if data["online"]:
                        embed = self.bot.embed(ctx.author)
                        embed.title = f"Status serwera Minecraft: {domain}"
                        if "version" in data:
                            embed.add_field(name="🔌 Wersja", value=data["version"])
                        if "players" in data:
                            embed.add_field(
                                name="👥 Liczba graczy",
                                value="{0}/{1}".format(
                                    data["players"]["online"], data["players"]["max"]
                                ),
                            )
                        if "map" in data:
                            embed.add_field(name="🌍 Mapa", value=data["map"])
                        if "software" in data:
                            embed.add_field(name="🗜 Silnik", value=data["software"])
                        if "motd" in data:
                            embed.add_field(
                                name="🔠 MOTD",
                                value="```yml\n"
                                + "\n".join(data["motd"]["clean"])
                                + "\n```",
                                inline=False,
                            )
                        if "icon" in data:
                            embed.set_thumbnail(url="attachment://logo.png")
                            image = base64.b64decode(
                                data["icon"].replace("data:image/png;base64,", "")
                            )
                            await ctx.send(
                                embed=embed,
                                file=discord.File(BytesIO(image), filename="logo.png"),
                            )
                        else:
                            await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ Podany serwer nie istnieje lub jest offline!")
                else:
                    raise commands.CommandError(await r.text())

    @minecraft.command()
    async def skin(self, ctx, nick: is_minecraft_nick):
        mojang = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{nick}")
        if mojang.status_code == 200:
            data = mojang.json()
            skin = requests.get(f"https://crafatar.com/renders/body/{data['id']}")
            if skin.status_code == 200:
                await ctx.send(
                    file=discord.File(BytesIO(skin.content), filename="skin.png")
                )
            else:
                raise commands.CommandError(skin.text)
        elif mojang.status_code == 204:
            await ctx.send("❌ Podany gracz nie został odnaleziony.")
        else:
            raise commands.CommandError(mojang.text)

    @commands.command(
        description="Statystyki w grze Fortnite\n\nPrzykład użycia: &fortnite epic liamdj23",
        usage="<epic/psn/xbl> <nick>",
    )
    async def fortnite(self, ctx, platform: is_platform, *, nick: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://fortnite-api.com/v1/stats/br/v2?name={quote(nick)}&accountType={platform}"
            ) as r:
                if r.status == 404:
                    await ctx.send(
                        "❌ Gracz **{}** nie istnieje lub nie grał w Fortnite!".format(
                            nick
                        )
                    )
                elif r.status == 200:
                    json = await r.json()
                    data = json["data"]["stats"]["all"]["overall"]
                    embed = self.bot.embed(ctx.author)
                    embed.title = "Statystyki w grze Fortnite"
                    embed.description = "🧑 Gracz: **{}**".format(nick)
                    embed.add_field(name="🏆 Wygrane", value=data["wins"])
                    embed.add_field(name="⚔ Zabójstwa", value=data["kills"])
                    embed.add_field(name="☠ Śmierci", value=data["deaths"])
                    embed.add_field(name="🕹Rozegranych meczy", value=data["matches"])
                    await ctx.send(embed=embed)
                else:
                    raise commands.CommandError(await r.text())

    @commands.command(
        description="Statystyki w grze CS:GO\n\nPrzykład użycia:\n&csgo https://steamcommunity.com/id/liamxdev/",
        usage="<link do profilu steam>",
        aliases=["cs"],
    )
    async def csgo(self, ctx, url: str):
        if "steamcommunity.com/id/" in url or "steamcommunity.com/profiles/" in url:
            try:
                steam_id, nick = await steam_resolve_url(url, self.bot.config["steam"])
            except TypeError:
                await ctx.send("❌ Nie odnaleziono podanego gracza.")
                return
        else:
            raise commands.BadArgument
        stats = await steam_get_stats(730, self.bot.config["steam"], steam_id)
        if not stats:
            await ctx.send(
                "❌ Wystąpił błąd przy pobieraniu informacji. Sprawdź czy podany profil jest publiczny"
                " i spróbuj ponownie."
            )
            return
        embed = self.bot.embed(ctx.author)
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
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))
