import mongoengine
from influxdb import InfluxDBClient
from discord.ext import commands

from cogs.fun import Fun
from cogs.ping import Ping
from cogs.admin import Admin
from settings import Settings

from logger import logger
from database.stats import Stats

from dashboard.server import Dashboard


class Atorin(commands.Bot):
    def __init__(self, **kwargs):
        super(Atorin, self).__init__(command_prefix="&", **kwargs)
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

        @self.event
        async def on_message(message):
            ctx = await self.get_context(message)
            if ctx.author.bot and ctx.author.id == 742076835549937805:
                pass
            elif ctx.author.bot:
                return
            self.stats.commands_usage(ctx.author.id, ctx.guild.id, ctx.command.name)
            await self.invoke(ctx)

        @self.event
        async def on_connect():
            self.log.info("Successfully connected to Discord API.")

        @self.event
        async def on_ready():
            self.log.info("Atorin is ready.")

    async def run(self, *args, **kwargs):
        await super(Atorin, self).start(self.settings.main["token"])
