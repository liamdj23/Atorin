import discord
from discord.ext import commands


class Premium(commands.Cog, name="💎 Premium"):
    def __init__(self, bot):
        self.bot = bot

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
