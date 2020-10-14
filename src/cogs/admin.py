from discord.ext import commands
import discord


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member):
        await ctx.guild.kick(member)
        await ctx.send(f"🦶 {member.mention} został wyrzucony przez {ctx.author.mention}")

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do wyrzucania użytkowników.")
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Bot nie ma uprawnień do wyrzucania użytkowników.")
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tę komendę możesz użyć tylko na serwerze.")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: &kick <użytkownik>")
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Nie znaleziono użytkownika o podanej nazwie.")
        self.bot.log.error(error)

