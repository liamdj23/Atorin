import discord
from discord.ext import commands


class Admin(commands.Cog, name="🛠 Administracyjne"):
    def __init__(self, bot):
        self.bot = bot
        self.bool_to_state = bot.utils.bool_to_state
        self.state_to_bool = bot.utils.state_to_bool

    @commands.command(aliases=["delmsg", "purge"],
                      usage="<1-100>",
                      description="Wpisz aby usunąć dużą ilość wiadomości\n\nPrzykład użycia: &clear 34")
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def clear(self, ctx, count: int):
        messages = await ctx.channel.purge(limit=count)
        await ctx.send("🗑 {} usunął **{}** wiadomości ✅".format(ctx.message.author.mention, len(messages)))

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
        embed = self.bot.embed(ctx.author)
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

    @commands.command(description="Otrzymywanie powiadomień o usuniętych i edytowanych wiadomościach")
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def logs(self, ctx, state: str = None, channel: discord.TextChannel = None):
        server = self.bot.mongo.Server.objects(id=ctx.guild.id).first()
        if not server:
            server = self.bot.mongo.Server(id=ctx.guild.id,
                                           logs=self.bot.mongo.Logs(enabled=False))
        if state is None:
            embed = self.bot.embed(ctx.author)
            embed.title = "Powiadomienia o usuniętych i edytowanych wiadomościach"
            if server.logs.enabled:
                embed.add_field(name="💬 Powiadomienia", value=self.bool_to_state(True))
                if server.logs.channel:
                    embed.add_field(name="📝 Kanał", value=ctx.guild.get_channel(int(server.logs.channel)).mention)
                embed.description = "💡 Aby wyłączyć powiadomienia o zdarzeniach, wpisz `&logs off`"
            else:
                embed.add_field(name="💬 Powiadomienia", value=self.bool_to_state(False))
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
        await ctx.send("Powiadomienia o usuniętych i edytowanych wiadomościach: " + self.bool_to_state(state_bool))

    @logs.error
    async def logs_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: `&logs on #nazwa_kanału` lub `&logs off`")
            return
        self.bot.log.error(error)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        server = self.bot.mongo.Server.objects(id=message.guild.id).first()
        if server and server.logs.enabled:
            channel = message.guild.get_channel(server.logs.channel)
            if channel:
                embed = self.bot.embed()
                embed.title = "Usunięta wiadomość"
                embed.add_field(name="🧑 Autor", value=message.author, inline=False)
                embed.add_field(name="✍️Treść", value="```{}```".format(message.clean_content), inline=False)
                await message.guild.get_channel(server.logs.channel).send(embed=embed)
            else:
                server.logs.enabled = False
                server.save()

    @commands.Cog.listener()
    async def on_message_edit(self, old, new):
        if old.content != new.content:
            server = self.bot.mongo.Server.objects(id=old.guild.id).first()
            if server and server.logs.enabled:
                channel = old.guild.get_channel(server.logs.channel)
                if channel:
                    embed = self.bot.embed()
                    embed.title = "Edytowana wiadomość"
                    embed.add_field(name="🧑 Autor", value=old.author, inline=False)
                    embed.add_field(name="❎ Poprzednia treść", value="```{}```".format(old.clean_content), inline=False)
                    embed.add_field(name="✅ Aktualna treść", value="```{}```".format(new.clean_content), inline=False)
                    await old.guild.get_channel(server.logs.channel).send(embed=embed)
                else:
                    server.logs.enabled = False
                    server.save()

    @commands.command(description="Zbanuj użytkownika",
                      usage="@uzytkownik <powód>")
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason: str):
        await member.ban(delete_message_days=0)
        await ctx.send("🔨 {} **zbanował** {} z powodu `{}`".format(
            ctx.author.mention,
            member.name + "#" + member.discriminator,
            reason
        ))
        await member.send("🔨 Zostałeś zbanowany na serwerze {} przez {} z powodu `{}`".format(
            ctx.guild.name, ctx.author.mention, reason))

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: `&ban @użytkownik <powód>`")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tej komendy można użyć tylko na serwerze!")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&ban @użytkownik <powód>`")
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do banowania użytkowników")
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Atorin nie ma uprawnień do banowania użytkowników")
            return

    @commands.command(
        description="Odbanuj użytkownika",
        usage="<nick#0000>")
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        if not banned_users:
            await ctx.send("❌ Lista zbanowanych użytkowników jest pusta")
            return
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send("✅ {} odbanował {}".format(ctx.author.mention, member))
                return
        await ctx.send("❌ Nie odnaleziono użytkownika o podanej nazwie.")

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: `&unban <użytkownik>`")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tej komendy można użyć tylko na serwerze!")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&unban <użytkownik>`")
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do banowania użytkowników")
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Atorin nie ma uprawnień do banowania użytkowników")
            return

    @commands.command(description="Wyrzuć użytkownika", usage="@użytkownik <powód>")
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason: str):
        await member.kick(reason=reason)
        await ctx.send("🦶 {} wyrzucił {} z powodu {}".format(
            ctx.author.mention,
            member.name + "#" + member.discriminator,
            reason
        ))
        await member.send("🦶 Zostałeś wyrzucony z serwera {} przez {} z powodu `{}`".format(
            ctx.guild.name, ctx.author.mention, reason))

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: `&kick @użytkownik <powód>`")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tej komendy można użyć tylko na serwerze!")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&kick @użytkownik <powód>`")
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do wyrzucania użytkowników")
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Atorin nie ma uprawnień do wyrzucania użytkowników")
            return

    @commands.command(description="Wycisza podanego użytkownika", aliases=["wycisz"], usage="@uzytkownik <powód>")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        mutedrole = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mutedrole:
            mutedrole = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                if channel.permissions_for(ctx.guild.get_member(self.bot.user.id)).manage_roles:
                    await channel.set_permissions(mutedrole, speak=False, send_messages=False)
        await member.add_roles(mutedrole, reason=reason)
        if reason:
            await ctx.send("🔇 Wyciszono {} z powodu `{}`".format(member.mention, reason))
            await member.send("🔇 Wyciszono Cię na serwerze **{}** z powodu `{}`".format(ctx.guild.name, reason))
        else:
            await ctx.send("🔇 Wyciszono {}".format(member.mention))
            await member.send("🔇 Wyciszono Cię na serwerze **{}**".format(ctx.guild.name))

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: `&mute @użytkownik <powód>`")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tej komendy można użyć tylko na serwerze!")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&mute @użytkownik <powód>`")
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do zarządzania wiadomościami")
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Atorin nie ma uprawnień do tworzenia ról")
            return
        self.bot.log.error(error)

    @commands.command(description="Odcisza podanego użytkownika", aliases=["odcisz"], usage="@uzytkownik")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        mutedrole = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(mutedrole)
        await ctx.send("🔊 Odciszono **{}**".format(member.mention))
        await member.send("🔊 Odciszono Cię na serwerze **{}**".format(ctx.guild.name))

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: `&unmute @użytkownik`")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tej komendy można użyć tylko na serwerze!")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&unmute @użytkownik`")
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do zarządzania wiadomościami")
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Atorin nie ma uprawnień do tworzenia ról")
            return

    @commands.command(description="Przyznaje ostrzeżenie użytkownikowi", aliases=["ostrzeżenie", "ostrzezenie"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        warning = self.bot.mongo.Warns(
            server=ctx.guild.id,
            member=member.id,
            given_by=ctx.author.id,
            reason=reason
        )
        warning.save()
        embed = self.bot.embed(ctx.author)
        embed.title = "Ostrzeżenie"
        if reason:
            embed.description = "⚠️{} został ostrzeżony przez {} z powodu `{}`".format(
                member.mention, ctx.author.mention, reason)
        else:
            embed.description = "⚠️{} został ostrzeżony przez {}".format(member.mention, ctx.author.mention)
        embed.color = discord.Color.gold()
        await ctx.send(embed=embed)

    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: `&warn @użytkownik <powód>`")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tej komendy można użyć tylko na serwerze!")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&warn @użytkownik <powód>`")
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Musisz być administratorem tego serwera!")
            return

    @commands.command(description="Pokazuje przyznane ostrzeżenia podanemu użytkownikowi",
                      aliases=["ostrzeżenia", "ostrzezenia"], usage="@użytkownik")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def warns(self, ctx, member: discord.Member):
        warns = self.bot.mongo.Warns.objects(server=ctx.guild.id, member=member.id)
        if len(warns) == 0:
            await ctx.send("✅ Brak ostrzeżeń")
            return
        embed = self.bot.embed(ctx.author)
        embed.title = "Ostrzeżenia"
        embed.description = "**{}** otrzymał/a **{}** {}\n\n".format(
            member, len(warns), "ostrzeżenie" if len(warns) == 1 else "ostrzeżenia")
        i = 0
        for warn in warns:
            i += 1
            embed.description += "{}. `{}` od <@{}>\n".format(i, warn.reason, warn.given_by)
        embed.color = discord.Color.gold()
        await ctx.send(embed=embed)

    @warns.error
    async def warns_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Poprawne użycie: `&warns @użytkownik`")
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tej komendy można użyć tylko na serwerze!")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&warns @użytkownik`")
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Musisz być administratorem tego serwera!")
            return
