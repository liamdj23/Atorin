from discord.ext import commands
import discord
from io import BytesIO


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def avatar(self, ctx, *, user: discord.User):
        avatar = await user.avatar_url.read()
        await ctx.send(file=discord.File(BytesIO(avatar), filename=user.name + ".png"))

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&avatar @użytkownik`")
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Nie znaleziono użytkownika o podanej nazwie.")
        if isinstance(error, discord.HTTPException):
            await ctx.send("❌ Wystąpił błąd przy pobieraniu avatara, spróbuj ponownie.")
        self.bot.log.error(error)