import mongoengine
from influxdb import InfluxDBClient
from discord.ext import commands
import discord
from datetime import datetime

from cogs.fun import Fun
from cogs.ping import Ping
from cogs.admin import Admin
from cogs.info import Info
from cogs.games import Games

from settings import Settings

from logger import logger
from database.stats import Stats

from dashboard.server import Dashboard


class Atorin(commands.Bot):
    def __init__(self, **kwargs):
        intents = discord.Intents.default()
        intents.members = True
        super(Atorin, self).__init__(command_prefix="&", intents=intents, **kwargs)
        self.settings = Settings()
        self.mongo = mongoengine.connect('atorin')
        self.influx = InfluxDBClient(database="atorin")
        self.influx.create_database("atorin")
        self.influx.switch_database("atorin")
        self.log = logger
        self.stats = Stats(self.influx)
        self.web = Dashboard()
        self.add_cog(Ping(self))
        self.add_cog(Fun(self))
        self.add_cog(Admin(self))
        self.add_cog(Info(self))
        self.add_cog(Games(self))

        @self.event
        async def on_message(message):
            ctx = await self.get_context(message)
            if ctx.author.bot and ctx.author.id == 742076835549937805:
                pass
            elif ctx.author.bot:
                return
            if ctx.command:
                await self.invoke(ctx)
                self.stats.commands_usage(ctx.author.id, ctx.guild.id, ctx.command.name)

        @self.event
        async def on_connect():
            self.log.info("Successfully connected to Discord API.")

        @self.event
        async def on_ready():
            self.log.info("Atorin is ready.")

    async def embed(self):
        embed = discord.Embed()
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text="Atorin", icon_url=str(self.user.avatar_url))
        embed.colour = discord.Colour(0xc4c3eb)
        return embed

    async def run(self, *args, **kwargs):
        await super(Atorin, self).start(self.settings.main["token"])

