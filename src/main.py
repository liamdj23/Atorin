import discord
from discord.ext import commands
import os


class Atorin(commands.Bot):
    def __init__(self, **kwargs):
        super(Atorin, self).__init__(command_prefix="&", **kwargs)


if __name__ == '__main__':
    bot = Atorin()


    @bot.event
    async def on_ready():
        print("Bot is ready")


    @bot.command()
    async def ping(ctx):
        await ctx.send("Pong!")


    @bot.event
    async def on_message(message):
        ctx = await bot.get_context(message)
        await bot.invoke(ctx)


    bot.run(os.environ["DISCORD_TOKEN"])
