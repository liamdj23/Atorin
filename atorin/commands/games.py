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
import humanize
import httpx

import aiohttp
import discord
from discord.ext import commands
from discord.commands import slash_command, Option, OptionChoice

from atorin.bot import Atorin
from ..config import config


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
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v1",
            params={"vanityurl": nick, "key": key},
        )
    if r.status_code == 200:
        data = r.json()
        if "steamid" not in data["response"]:
            return None
        return data["response"]["steamid"], nick


async def steam_get_stats(app_id: int, key: str, steam_id: int):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/",
            params={"appid": app_id, "key": key, "steamid": steam_id},
        )
    if r.status_code == 200:
        data = r.json()
        if "playerstats" in data and "stats" in data["playerstats"]:
            return data["playerstats"]["stats"]


class Games(commands.Cog, name="🕹 Gry"):
    def __init__(self, bot: Atorin):
        self.bot = bot

    @slash_command(
        description="Status of Minecraft server",
        description_localizations={"pl": "Status serwera Minecraft"},
        guild_ids=config["guild_ids"],
    )
    async def mcsrv(
        self,
        ctx: discord.ApplicationContext,
        domain: Option(
            str,
            name="address",
            name_localizations={"pl": "adres"},
            description="Server address",
            description_localizations={"pl": "Adres serwera"},
        ),
    ):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://api.mcsrvstat.us/2/{domain}")
            data = r.json()
            if not data["online"]:
                r = await client.get(f"https://api.mcsrvstat.us/bedrock/2/{domain}")
                data = r.json()
                if not data["online"]:
                    raise commands.BadArgument(
                        "Adres serwera jest niepoprawny lub serwer jest offline!"
                        if ctx.interaction.locale == "pl"
                        else "Server address is not valid or server is offline!"
                    )
        embed = discord.Embed()
        embed.title = (
            f"Status serwera Minecraft: {domain}"
            if ctx.interaction.locale == "pl"
            else f"Minecraft server status: {domain}"
        )
        if "version" in data:
            embed.add_field(
                name="⚙️ Wersja" if ctx.interaction.locale == "pl" else "⚙️ Version", value=data["version"]
            )
        if "players" in data:
            embed.add_field(
                name="👥 Liczba graczy" if ctx.interaction.locale == "pl" else "👥 Players",
                value=f"{data['players']['online']}/{data['players']['max']}",
            )
        if "software" in data:
            embed.add_field(
                name="🗜 Silnik" if ctx.interaction.locale == "pl" else "🗜 Software",
                value=f"`{data['software']}`",
                inline=False,
            )
        if "plugins" in data:
            embed.add_field(
                name="🔌 Pluginy" if ctx.interaction.locale == "pl" else "🔌 Plugins",
                value=f"`{', '.join(data['plugins']['names'])}`",
                inline=False,
            )
        if "motd" in data:
            embed.add_field(
                name="🔠 MOTD",
                value="```yml\n" + "\n".join(data["motd"]["clean"]).strip() + "\n```",
                inline=False,
            )
        embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{domain}")
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Show your skin in Minecraft",
        description_localizations={"pl": "Wysyła Twojego skina w Minecraft"},
        guild_ids=config["guild_ids"],
    )
    async def mcskin(
        self,
        ctx: discord.ApplicationContext,
        nick: Option(
            str,
            name="nickname",
            name_localizations={"pl": "nick"},
            description="Your nickname in Minecraft",
            description_localizations={"pl": "Twój nick w Minecraft"},
        ),
    ):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            mojang = await client.get(f"https://api.mojang.com/users/profiles/minecraft/{nick}")
        if mojang.status_code == 200:
            data = mojang.json()
            async with httpx.AsyncClient() as client:
                skin = await client.get(f"https://crafatar.com/renders/body/{data['id']}")
            if skin.status_code == 200:
                embed = discord.Embed()
                embed.title = (
                    f"Skin {nick} w Minecraft" if ctx.interaction.locale == "pl" else f"{nick}'s skin in Minecraft"
                )
                embed.set_image(url="attachment://skin.png")
                await ctx.send_followup(
                    embed=embed,
                    files=[discord.File(BytesIO(skin.content), filename="skin.png")],
                )
            else:
                raise commands.CommandError(skin.text)
        elif mojang.status_code == 204:
            raise commands.BadArgument(
                "Nie znaleziono podanego gracza!" if ctx.interaction.locale == "pl" else "Player not found!"
            )
        else:
            raise commands.CommandError(mojang.text)

    @slash_command(
        description="Your statistics in Fortnite",
        description_localizations={"pl": "Twoje statystyki w grze Fortnite"},
        guild_ids=config["guild_ids"],
    )
    async def fortnite(
        self,
        ctx: discord.ApplicationContext,
        platform: Option(
            str,
            name="platform",
            name_localizations={"pl": "platforma"},
            description="Select platform you are playing on",
            description_localizations={"pl": "Wybierz platformę na której grasz"},
            choices=[
                OptionChoice("Epic Games", "epic"),
                OptionChoice("Playstation Network", "psn"),
                OptionChoice("Xbox Live", "xbl"),
            ],
        ),
        nick: Option(
            str,
            name="nickname",
            name_localizations={"pl": "nick"},
            description="Your nickname in Fortnite",
            description_localizations={"pl": "Twój nick w Fortnite"},
        ),
    ):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get(
                url="https://fortnite-api.com/v2/stats/br/v2",
                params={"name": nick, "accountType": platform},
                headers={"Authorization": config["fortnite"]},
            )
        if r.status_code == 200:
            json = r.json()
            data = json["data"]["stats"]["all"]["overall"]
            embed = discord.Embed()
            embed.title = "Statystyki w grze Fortnite" if ctx.interaction.locale == "pl" else "Statistics in Fortnite"
            embed.description = f"🧑 Gracz: **{nick}**" if ctx.interaction.locale == "pl" else f"🧑 Player: **{nick}**"
            embed.add_field(
                name="⭐️ Punkty" if ctx.interaction.locale == "pl" else "⭐️ Score",
                value=humanize.intcomma(data["score"]),
            )
            embed.add_field(
                name="🏆 Wygrane" if ctx.interaction.locale == "pl" else "🏆 Wins", value=humanize.intcomma(data["wins"])
            )
            embed.add_field(
                name="⚔ Zabójstwa" if ctx.interaction.locale == "pl" else "⚔ Kills",
                value=humanize.intcomma(data["kills"]),
            )
            embed.add_field(
                name="☠ Śmierci" if ctx.interaction.locale == "pl" else "☠ Deaths",
                value=humanize.intcomma(data["deaths"]),
            )
            embed.add_field(
                name="🕹 Rozegranych meczy" if ctx.interaction.locale == "pl" else "🕹 Matches played",
                value=humanize.intcomma(data["matches"]),
            )
            await ctx.send_followup(embed=embed)
        elif r.status_code == 403:
            raise commands.BadArgument(
                f"Statystyki gracza __{nick}__ są **prywatne**!"
                if ctx.interaction.locale == "pl"
                else f"Statistics of __{nick}__ are **private**!"
            )
        elif r.status_code == 404:
            raise commands.BadArgument(
                "Podany gracz nie istnieje lub nigdy nie grał w Fortnite!"
                if ctx.interaction.locale == "pl"
                else "Player not found or never played Fortnite!"
            )
        else:
            raise commands.CommandError(r.text)

    @slash_command(
        description="Your statistics in CS:GO",
        description_localizations={"pl": "Twoje statystyki w grze CS:GO"},
        guild_ids=config["guild_ids"],
    )
    async def csgo(
        self,
        ctx: discord.ApplicationContext,
        url: Option(
            str,
            name="url",
            name_localizations={"pl": "link"},
            description="URL to your Steam profile",
            description_localizations={"pl": "Link do Twojego profilu Steam"},
        ),
    ):
        await ctx.defer()
        if "steamcommunity.com/id/" in url or "steamcommunity.com/profiles/" in url:
            try:
                steam_id, nick = await steam_resolve_url(url, config["steam"])
            except TypeError:
                raise commands.BadArgument(
                    "Nie odnaleziono podanego gracza!" if ctx.interaction.locale == "pl" else "Player not found!"
                )
        else:
            raise commands.BadArgument(
                "Podany link jest nieprawidłowy!" if ctx.interaction.locale == "pl" else "URL is not valid!"
            )
        stats = await steam_get_stats(730, config["steam"], steam_id)
        if not stats:
            raise commands.BadArgument(
                "Podany profil musi być publiczny!" if ctx.interaction.locale == "pl" else "Profile must be public!"
            )
        embed = discord.Embed()
        embed.title = "Statystyki w grze CS:GO" if ctx.interaction.locale == "pl" else "Statistics in CS:GO"
        embed.description = f"🧑 Gracz: **{nick}**" if ctx.interaction.locale == "pl" else f"🧑 Player: **{nick}**"
        for i in stats:
            if i["name"] == "total_kills":
                embed.add_field(
                    name="🔫 Liczba zabójstw" if ctx.interaction.locale == "pl" else "🔫 Kills", value=i["value"]
                )
            elif i["name"] == "total_deaths":
                embed.add_field(
                    name="☠ Liczba śmierci" if ctx.interaction.locale == "pl" else "☠ Deaths", value=i["value"]
                )
            elif i["name"] == "total_matches_played":
                embed.add_field(
                    name="⚔ Rozegranych meczy" if ctx.interaction.locale == "pl" else "⚔ Matches played",
                    value=i["value"],
                )
            elif i["name"] == "total_matches_won":
                embed.add_field(
                    name="🏆 Wygranych meczy" if ctx.interaction.locale == "pl" else "🏆 Matches won",
                    value=i["value"],
                    inline=False,
                )
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Your statistics in League of Legends",
        description_localizations={"pl": "Twoje statystki w grze League of Legends"},
        guild_ids=config["guild_ids"],
    )
    async def lol(
        self,
        ctx: discord.ApplicationContext,
        region: Option(
            str,
            name="region",
            name_localizations={"pl": "region"},
            description="Select region you are playing on",
            description_localizations={"pl": "Wybierz region na którym grasz"},
            choices=[
                OptionChoice("EUNE", "eun1"),
                OptionChoice("BR", "br1"),
                OptionChoice("EUW", "euw1"),
                OptionChoice("JP", "jp1"),
                OptionChoice("KR", "kr"),
                OptionChoice("LAN", "la1"),
                OptionChoice("LAS", "la2"),
                OptionChoice("NA", "na1"),
                OptionChoice("OCE", "oc1"),
                OptionChoice("RU", "ru"),
                OptionChoice("TR", "tr1"),
            ],
        ),
        nick: Option(
            str,
            name="nickname",
            name_localizations={"pl": "nick"},
            description="Your nickname in League of Legends",
            description_localizations={"pl": "Twój nick w League of Legends"},
        ),
    ):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{nick}",
                params={"api_key": config["lol"]},
            )
            if r.status_code == 404:
                raise commands.BadArgument(
                    "Nie znaleziono podanego gracza!" if ctx.interaction.locale == "pl" else "Player not found!"
                )
            summoner = r.json()
            r2 = await client.get(
                f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner['id']}",
                params={"api_key": config["lol"]},
            )
        stats = r2.json()
        embed = discord.Embed()
        embed.title = (
            "Statystyki w grze League of Legends"
            if ctx.interaction.locale == "pl"
            else "Statistics in League of Legends"
        )
        embed.description = (
            f"🧑 Gracz: **{summoner['name']}**\n🏆 Poziom: **{summoner['summonerLevel']}**\n🌍 Region: **{region}**"
            if ctx.interaction.locale == "pl"
            else f"🧑 Player: **{summoner['name']}**\n🏆 Level: **{summoner['summonerLevel']}**\n🌍 Region: **{region}**"
        )
        embed.set_thumbnail(
            url=f"https://ddragon.leagueoflegends.com/cdn/10.15.1/img/profileicon/{summoner['profileIconId']}.png"
        )
        for gamemode in stats:
            value = ""
            if "tier" in gamemode:
                value += f"🎌 **{'Ranga' if ctx.interaction.locale == 'pl' else 'Rank'}:** `{gamemode['tier']} {gamemode['rank']}`\n"
            value += f"✅ **{'Wygrane' if ctx.interaction.locale == 'pl' else 'Wins'}:** `{gamemode['wins']}`\n"
            value += f"❌ **{'Przegrane' if ctx.interaction.locale == 'pl' else 'Losses'}:** `{gamemode['losses']}`\n"
            embed.add_field(
                name=f"🏟 {'Tryb gry' if ctx.interaction.locale == 'pl' else 'Gamemode'}: `{gamemode['queueType'].replace('_', ' ')}`",
                value=value,
            )
        await ctx.send_followup(embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))
