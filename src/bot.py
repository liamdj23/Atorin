import json
import os
from datetime import datetime

import discord
import mongoengine
from discord.ext import commands
from loguru import logger
import asyncpraw

import models
import utils
from cogs.admin import Admin
from cogs.fun import Fun
from cogs.games import Games
from cogs.info import Info
from cogs.statcord import StatcordPost
from cogs.music import Music
from dashboard.flask import Dashboard
from events.guild import GuildEvents


class Atorin(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        intents = discord.Intents.default()
        intents.members = False
        super(Atorin, self).__init__(command_prefix="&", help_command=None, intents=intents, **kwargs)
        mongoengine.connect('atorin', host="mongo")
        self.mongo = models
        with open(os.path.dirname(__file__) + "/../config.json", 'r') as config:
            self.config = json.load(config)
        self.reddit = asyncpraw.Reddit(
            client_id=self.config["reddit_id"],
            client_secret=self.config["reddit_secret"],
            user_agent="Atorin")
        self.log = logger
        self.utils = utils
        self.web = Dashboard(self)
        self.guild_events = GuildEvents(self)
        self.add_cog(Fun(self))
        self.add_cog(Admin(self))
        self.add_cog(Info(self))
        self.add_cog(Games(self))
        self.add_cog(StatcordPost(self))
        self.add_cog(Music(self))

        @self.event
        async def on_command_error(ctx, error):
            command = ctx.command
            if isinstance(error, commands.NoPrivateMessage):
                await ctx.send("❌ Tę komendę możesz użyć tylko na serwerze.")
                return
            elif isinstance(error, commands.BadArgument):
                await ctx.send(f"❌ Poprawne użycie: `&{command.name} {command.usage}`")
                return
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(f"❌ Poprawne użycie: `&{command.name} {command.usage}`")
                return
            elif isinstance(error, commands.UserNotFound):
                await ctx.send("❌ Nie znaleziono podanego użytkownika.")
                return
            elif isinstance(error, commands.CommandNotFound):
                return
            else:
                await ctx.send("❌ Wystąpił błąd wewnętrzny, spróbuj ponownie później."
                               " Jeśli błąd się powtarza, skontaktuj się z autorem na serwerze Discord "
                               "https://discord.gg/Ygr5wAZbsZ")
                self.log.error(error)
                return

        @self.event
        async def on_shard_connect(id):
            print("\033[94m * Shard {} successfully connected to Discord API.".format(id), flush=True)

        @self.event
        async def on_shard_ready(id):
            print("\033[96m * Shard {} is ready.".format(id), flush=True)
            await self.update_status()

        @self.event
        async def on_ready():
            print("\033[92m * Running with {} shards".format(len(self.shards)), flush=True)
            print("\033[1m * Atorin is ready.", flush=True)
            self.web.start()

    def embed(self, author=None):
        embed = discord.Embed()
        embed.timestamp = datetime.utcnow()
        if author and self.mongo.Premium.objects(id=author.id).first():
            embed.set_footer(text="Atorin Premium 💎", icon_url=str(self.user.avatar_url))
        else:
            embed.set_footer(text="Atorin", icon_url=str(self.user.avatar_url))
        embed.colour = discord.Colour(0xc4c3eb)
        return embed

    def avatar(self):
        return self.avatar()

    async def update_status(self):
        await self.change_presence(activity=discord.Game(name="z {} serwerami | &help | Dołącz do serwera Discord!".format(len(self.guilds))))

    def run(self, *args, **kwargs):
        super(Atorin, self).run(self.config["bot"])

