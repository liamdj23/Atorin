import mongoengine
from discord.ext import commands
import logging

from cogs.fun import Fun
from cogs.ping import Ping
from settings import Settings

logger = logging.getLogger(__name__)
log_formatter = logging.Formatter('%(asctime)s [%(filename)s|%(funcName)s] -%(levelname)s- :: %(message)s ')
err_handler = logging.StreamHandler()
err_handler.setLevel(logging.ERROR)
err_handler.setFormatter(log_formatter)
logger.addHandler(err_handler)


class Atorin(commands.Bot):
    def __init__(self, **kwargs):
        super(Atorin, self).__init__(command_prefix="&", **kwargs)
        self.settings = Settings()
        self.mongo = mongoengine.connect('atorin')
        self.log = logger
        self.add_cog(Ping(self))
        self.add_cog(Fun(self))

        @self.event
        async def on_message(message):
            ctx = await self.get_context(message)
            await self.invoke(ctx)

    def run(self, *args, **kwargs):
        super(Atorin, self).run(self.settings.main["token"])
