import json
import os
import sys
from datetime import datetime
import time

import discord
import mongoengine
from discord.ext import commands
from loguru import logger
import asyncpraw
from pyfiglet import Figlet

import models
import utils
from dashboard.flask import Dashboard
from events.guild import GuildEvents


class Atorin(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        f = Figlet()
        print(f.renderText("ATORIN"), flush=True)
        print("\033[95m * Starting Atorin...", flush=True)
        intents = discord.Intents.default()
        intents.members = False
        super(Atorin, self).__init__(
            command_prefix="&", help_command=None, intents=intents, **kwargs
        )
        with open(os.path.dirname(__file__) + "/../config.json", "r") as config:
            self.config = json.load(config)
        try:
            mongoengine.connect("atorin", host=self.config["mongo_host"])
            print("\033[92m * Connected to MongoDB.", flush=True)
        except Exception as e:
            print("\033[91m * Can't connect to MongoDB, shutting down...", flush=True)
            print(f"\033[91m :: {e}", flush=True)
            sys.exit(1)
        self.mongo = models
        self.reddit = asyncpraw.Reddit(
            client_id=self.config["reddit_id"],
            client_secret=self.config["reddit_secret"],
            user_agent="Atorin",
        )
        self.log = logger
        self.utils = utils
        self.web = Dashboard(self)
        self.guild_events = GuildEvents(self)

        @self.event
        async def on_command_error(ctx, error):
            command = ctx.command
            embed = self.embed(ctx.author)
            embed.colour = 0xFF0000
            if isinstance(error, commands.NoPrivateMessage):
                embed.description = "❌ Tę komendę możesz użyć tylko na serwerze."
                await ctx.send(embed=embed)
                return
            elif isinstance(error, commands.BadArgument):
                embed.description = (
                    f"❌ Poprawne użycie: `&{command.name} {command.usage}`"
                )
                await ctx.send(embed=embed)
                return
            elif isinstance(error, commands.MissingRequiredArgument):
                embed.description = (
                    f"❌ Poprawne użycie: `&{command.name} {command.usage}`"
                )
                await ctx.send(embed=embed)
                return
            elif isinstance(error, commands.UserNotFound):
                embed.description = "❌ Nie znaleziono podanego użytkownika."
                await ctx.send(embed=embed)
                return
            elif isinstance(error, commands.CommandNotFound):
                return
            elif isinstance(error, commands.MissingPermissions):
                if "ban_members" in error.missing_perms:
                    embed.description = (
                        "❌ Nie masz uprawnień do banowania użytkowników."
                    )
                elif "manage_messages" in error.missing_perms:
                    embed.description = (
                        "❌ Nie masz uprawnień do zarządzania wiadomościami."
                    )
                elif "administrator" in error.missing_perms:
                    embed.description = "❌ Nie jesteś administratorem tego serwera."
                elif "kick_members" in error.missing_perms:
                    embed.description = (
                        "❌ Nie masz uprawnień do wyrzucania użytkowników."
                    )
                else:
                    embed.description = (
                        "❌ Nie masz odpowiednich uprawnień do wykonania tej komendy. Wymagane "
                        f"uprawnienia: `{','.join(error.missing_perms)}` "
                    )
                    self.log.error(error.missing_perms)
                await ctx.send(embed=embed)
            elif isinstance(error, commands.BotMissingPermissions):
                if "ban_members" in error.missing_perms:
                    embed.description = (
                        "❌ Atorin nie ma uprawnień do banowania użytkowników."
                    )
                elif "manage_messages" in error.missing_perms:
                    embed.description = (
                        "❌ Atorin nie ma uprawnień do zarządzania wiadomościami."
                    )
                elif "kick_members" in error.missing_perms:
                    embed.description = (
                        "❌ Atorin nie ma uprawnień do wyrzucania użytkowników."
                    )
                elif "manage_roles" in error.missing_perms:
                    embed.description = (
                        "❌ Atorin nie ma uprawnień do zarządzania rolami."
                    )
                else:
                    embed.description = (
                        "❌ Bot nie ma odpowiednich uprawnień do wykonania tej komendy."
                        f" Wymagane uprawnienia: `{','.join(error.missing_perms)}`"
                    )
                    self.log.error(error.missing_perms)
                await ctx.send(embed=embed)
            elif isinstance(error, commands.CommandInvokeError):
                if isinstance(error.original, discord.Forbidden):
                    embed.description = (
                        "❌ Bot nie ma odpowiednich uprawnień do wykonania tej komendy."
                        " Przenieś wyżej rolę `Atorin` w ustawieniach serwera"
                        " i spróbuj ponownie."
                    )
                    await ctx.send(embed=embed)
                    return
                self.log.error(f"{command.name}: {error.original}")
            elif isinstance(error, commands.CommandOnCooldown):
                formatted_time = time.strftime(
                    "%M minut i %S sekund", time.gmtime(error.retry_after)
                )
                embed.description = f"❌ Możesz użyć tej komendy za {formatted_time}"
                await ctx.send(embed=embed)
            elif isinstance(error, discord.NotFound):
                embed.description = "❌ Podany zasób nie został odnaleziony."
                await ctx.send(embed=embed)
            else:
                self.log.error(f"{command.name}: {error}")
                embed.description = (
                    f"❌ Wystąpił błąd wewnętrzny, spróbuj ponownie później. Treść błędu: `{error}`"
                    " Jeśli błąd się powtarza, skontaktuj się z autorem na serwerze Discord "
                    "https://discord.gg/Ygr5wAZbsZ"
                )
                await ctx.send(embed=embed)

        @self.event
        async def on_shard_connect(id):
            print(
                "\033[94m * Shard {} successfully connected to Discord API.".format(id),
                flush=True,
            )

        @self.event
        async def on_shard_ready(id):
            print("\033[96m * Shard {} is ready.".format(id), flush=True)
            await self.update_status()

        @self.event
        async def on_ready():
            print(
                "\033[92m * Running with {} shards".format(len(self.shards)), flush=True
            )
            for file in os.listdir("cogs"):
                if file.endswith(".py"):
                    name = file[:-3]
                    try:
                        self.load_extension(f"cogs.{name}")
                        print(f"\033[95m * Loaded extension: {name}", flush=True)
                    except commands.errors.ExtensionAlreadyLoaded:
                        pass
            print("\033[1m * Atorin is ready.", flush=True)
            self.web.start()

    def embed(self, author=None):
        embed = discord.Embed()
        embed.timestamp = datetime.utcnow()
        embed.set_footer(
            text="❌ Ze względu na zmiany wprowadzone przez Discorda, od 1 marca 2022 komendy z prefixem & zostaną wyłączone. Proszę o używanie komend z ukośnikiem. W przypadku problemów, wejdź na serwer support Atorina",
            icon_url=str(self.user.avatar_url),
        )
        embed.colour = discord.Colour(0xC4C3EB)
        return embed

    def avatar(self):
        return self.avatar()

    async def update_status(self):
        await self.change_presence(
            activity=discord.Game(
                name="z {} serwerami | &help | Dołącz do serwera Discord!".format(
                    len(self.guilds)
                )
            )
        )

    def run(self, *args, **kwargs):
        super(Atorin, self).run(self.config["bot"])
