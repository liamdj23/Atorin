from discord.ext import commands


class Admin(commands.Cog, name="🛠 Administracyjne"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["delmsg", "purge"],
                      usage="<1-100>",
                      description="Wpisz aby usunąć dużą ilość wiadomości\n\nPrzykład użycia: &clear 34")
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def clear(self, ctx, count: int):
        messages = await ctx.channel.purge(limit=count)
        await ctx.send(f"🗑 Usunięto **{len(messages)}** wiadomości ✅")

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do zarządzania wiadomościami.")
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Bot nie ma uprawnień do zarządzania wiadomościami.")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tę komendę możesz użyć tylko na serwerze.")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: &clear <1-100>")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: &clear <1-100>")
            return
        self.bot.log.error(error)

    @commands.command(aliases=["ogłoszenie", "ogloszenie"], usage="<tekst>", description="Tworzy ogłoszenie")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def advert(self, ctx, *, content: str):
        embed = await self.bot.embed()
        embed.title = "📣 Ogłoszenie 📣"
        embed.description = content
        message = await ctx.send(embed=embed)
        await message.add_reaction("🔼")
        await message.add_reaction("🔽")

    @advert.error
    async def advert_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie jesteś administratorem tego serwera!")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tę komendę możesz użyć tylko na serwerze.")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: &advert <tekst>")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: &advert <tekst>")
            return
        self.bot.log.error(error)
