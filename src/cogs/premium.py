import discord
from discord.ext import commands


class Premium(commands.Cog, name="💎 Premium"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild and message.guild.id == 408960275933429760:
            if self.bot.mongo.Premium.objects(id=message.author.id).first():
                supporting_role = discord.utils.get(message.guild.roles, id=807643329067876383)
                await message.author.add_roles(supporting_role)

    @commands.command(description="Wysyła podaną wiadomość jako Atorin", usage="<tekst>", aliases=["echo"])
    async def say(self, ctx, *, content: commands.clean_content):
        if not self.bot.mongo.Premium.objects(id=ctx.author.id).first():
            await ctx.send("❌ Musisz posiadać **Atorin Premium** aby użyć tej komendy!")
            return
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.send(content)
