import discord
from discord.ext import commands
from discord.commands import slash_command, Option

from atorin.bot import Atorin

from ..utils import premium_only
from .. import database


class Premium(commands.Cog, name="💎 Premium"):
    def __init__(self, bot: Atorin):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild and message.guild.id == 408960275933429760:
            if database.premium.Premium.objects(id=message.author.id).first():
                supporting_role = discord.utils.get(
                    message.guild.roles, id=807643329067876383
                )
                await message.author.add_roles(supporting_role)

    @slash_command(
        description="Wysyła podaną wiadomość jako Atorin",
        guild_ids=[408960275933429760],
    )
    @premium_only()
    async def say(
        self, ctx: discord.ApplicationContext, content: Option(str, "Treść wiadomości")
    ):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.respond(content)


def setup(bot):
    bot.add_cog(Premium(bot))
