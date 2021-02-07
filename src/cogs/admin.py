from discord.ext import commands
import discord


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bool_to_state = bot.utils.bool_to_state
        self.state_to_bool = bot.utils.state_to_bool

    @commands.command(brief="Wyrzuć użytkownika",
                      description="Wpisz aby wyrzucić użytkownika z serwera")
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member):
        await ctx.guild.kick(member)
        await ctx.send(f"🦶 {member.mention} został wyrzucony przez {ctx.author.mention}")

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do wyrzucania użytkowników.")
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Bot nie ma uprawnień do wyrzucania użytkowników.")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tę komendę możesz użyć tylko na serwerze.")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: &kick <użytkownik>")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Nie znaleziono użytkownika o podanej nazwie.")
            return
        self.bot.log.error(error)

    @commands.command(brief="Banowanie użytkownika",
                      description="Wpisz aby zbanować użytkownika")
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        await ctx.guild.ban(member, reason=reason, delete_message_days=0)
        await ctx.send(f"⛔ **{str(member)}** został zbanowany przez **{str(ctx.author)}**")

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do banowania użytkowników.")
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Bot nie ma uprawnień do banowania użytkowników.")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tę komendę możesz użyć tylko na serwerze.")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: &ban <użytkownik> [powód]")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Nie znaleziono użytkownika o podanej nazwie.")
            return
        self.bot.log.error(error)

    @commands.command(brief="Odbanuj użytkownika",
                      description="Wpisz aby odbanować użytkownika")
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, *, member: str):
        ban_list = await ctx.guild.bans()
        for ban in ban_list:
            if ban.user.name.lower() == member.lower():
                await ctx.guild.unban(ban.user)
                await ctx.send(f"✅ **{ban.user.name}** został odbanowany przez **{str(ctx.author)}**")
                return
        raise commands.BadArgument

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do banowania użytkowników.")
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Bot nie ma uprawnień do banowania użytkowników.")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tę komendę możesz użyć tylko na serwerze.")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Nie znaleziono użytkownika na liście zbanowanych.")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: &unban <użytkownik>")
            return
        self.bot.log.error(error)

    @commands.command(aliases=["delmsg"], brief="Usuwanie wiadomości",
                      description="Wpisz usunąć dużą ilość wiadomości")
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

    @commands.command(brief="Powiadomienia o zdarzeniach",
                      description="Wpisz aby otrzymywać powiadomienia o zdarzeniach na serwerze")
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def logs(self, ctx, state: str = None, channel: discord.TextChannel = None):
        server = self.bot.mongo.Server.objects(id=ctx.guild.id).first()
        if not server:
            server = self.bot.mongo.Server(id=ctx.guild.id, logs=self.bot.mongo.Logs(enabled=False, events=["join", "leave"]))
        if state is None:
            embed = await self.bot.embed()
            embed.title = "Powiadomienia o zdarzeniach"
            if server.logs.enabled:
                embed.description = "💡 Aby zarządać powiadomieniami wejdź na " \
                                    "[stronę bota](https://bot.liamdj23.ovh/panel).\n" \
                                    "💡 Aby wyłączyć powiadomienia o zdarzeniach, wpisz " \
                                    "`&logs off`"
                embed.add_field(name="👋 Nowy członek:", value=self.bool_to_state("join" in server.logs.events))
                embed.add_field(name="💀 Opuszczenie serwera:", value=self.bool_to_state("leave" in server.logs.events))
                embed.add_field(name="🗑 Usunęcie wiadomości:", value=self.bool_to_state("message_delete" in server.logs.events))
            else:
                embed.add_field(name="💬 Powiadomienia:", value=self.bool_to_state(False))
                embed.description = "💡 Aby włączyć powiadomenia o zdarzeniach wpisz `&logs on #nazwa_kanału`"
            await ctx.send(embed=embed)
            return
        if self.state_to_bool(state) is None:
            raise commands.BadArgument
        if state == "on":
            if channel is None:
                raise commands.BadArgument
            server.logs.channel = channel.id
        if channel and not ctx.guild.me.permissions_in(channel).send_messages:
            await ctx.send("❌ Bot nie posiada uprawnień do wysyłania wiadomości na kanale " + channel.mention)
            return
        state_bool = self.state_to_bool(state)
        server.logs.enabled = state_bool
        server.save()
        await ctx.send("Powiadomienia o zdarzeniach: " + self.bool_to_state(state_bool))

    @logs.error
    async def logs_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: `&logs on #nazwa_kanału` lub `&logs off`")
            return
        self.bot.log.error(error)
