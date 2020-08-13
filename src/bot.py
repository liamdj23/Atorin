import mongoengine
from discord.ext import commands

from cogs.fun import Fun
from cogs.ping import Ping
from settings import Settings


class Atorin(commands.Bot):
    def __init__(self, **kwargs):
        super(Atorin, self).__init__(command_prefix="&", **kwargs)
        self.settings = Settings()
        self.mongo = mongoengine.connect('atorin')
        self.add_cog(Ping(self))
        self.add_cog(Fun(self))

        @self.event
        async def on_message(message):
            ctx = await self.get_context(message)
            await self.invoke(ctx)

    def run(self, *args, **kwargs):
        super(Atorin, self).run(self.settings.main["token"])
