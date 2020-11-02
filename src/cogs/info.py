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

    @commands.command()
    async def invite(self, ctx):
        await ctx.send("🔹 Dodaj Atorina na swój serwer, korzystając z tego linku:\n <https://liamdj23.ovh/addbot>")

    @commands.command()
    async def user(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = await self.bot.embed()
        embed.title = "Informacje o " + member.name + "#" + member.discriminator
        embed.add_field(name="🆔 ID", value=member.id)
        embed.add_field(name="🎭 Pseudonim", value=member.nick)
        embed.add_field(name="👶 Data utworzenia konta", value=member.created_at.replace(microsecond=0), inline=False)
        embed.add_field(name="🤝 Data dołączenia", value=member.joined_at.replace(microsecond=0))
        roles = ""
        for role in member.roles:
            roles += role.mention + ","
        embed.add_field(name="🏅 Role", value=roles)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)
