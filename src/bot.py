import mongoengine
from discord.ext import commands

from cogs.fun import Fun
from cogs.ping import Ping
from settings import Settings

from logger import logger

from dashboard.server import Dashboard


class Atorin(commands.Bot):
    def __init__(self, **kwargs):
        super(Atorin, self).__init__(command_prefix="&", **kwargs)
        self.settings = Settings()
        self.mongo = mongoengine.connect('atorin')
        self.log = logger
        self.web = Dashboard()
        self.add_cog(Ping(self))
        self.add_cog(Fun(self))

        @self.event
        async def on_message(message):
            ctx = await self.get_context(message)
            await self.invoke(ctx)

        @self.event
        async def on_connect():
            self.log.info("Successfully connected to Discord API.")

        @self.event
        async def on_ready():
            self.log.info("Atorin is ready.")

    async def run(self, *args, **kwargs):
        await super(Atorin, self).start(self.settings.main["token"])
