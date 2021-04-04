import statcord
from discord.ext import commands


class StatcordPost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.key = self.bot.config["statcord"]
        self.api = statcord.Client(self.bot, self.key)
        self.api.logger.disabled = True
        self.api.start_loop()

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.api.command_run(ctx)
