import datetime

import discord
from discord.ext import commands


class Admin(commands.Cog, name="🛠 Administracyjne"):
    def __init__(self, bot):
        self.bot = bot
        self.bool_to_state = bot.utils.bool_to_state
        self.state_to_bool = bot.utils.state_to_bool

    async def get_logs_channel(self, guild):
        server = self.bot.mongo.Server.objects(id=guild.id).first()
        if server and server.logs.enabled:
            channel = guild.get_channel(server.logs.channel)
            if not channel:
                server.logs.enabled = False
                server.save()
            return channel

    async def save_to_event_logs(self, guild, action, by, on, reason):
        self.bot.mongo.EventLogs(
            server=guild,
            action_name=action,
            action_by=by,
            action_on=on,
            reason=reason,
            date=datetime.datetime.now()
        ).save()

    @commands.command(aliases=["delmsg", "purge"],
                      usage="<3-100>",
                      description="Wpisz aby usunąć dużą ilość wiadomości\n\nPrzykład użycia: &clear 34")
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(read_message_history=True)
    @commands.guild_only()
    async def clear(self, ctx, limit: int):
        if limit <= 3 or limit >= 100:
            raise commands.BadArgument
        messages = []
        async for message in ctx.channel.history(limit=limit):
            messages.append(message)
        deleted = []
        try:
            deleted = await ctx.channel.purge(limit=limit)
        except discord.HTTPException:
            to_delete = [message for message in messages if message not in deleted]
            async for message in to_delete:
                await message.delete()
        await self.save_to_event_logs(ctx.guild.id, "clear", ctx.author.id, ctx.channel.id, None)
        await ctx.send("🗑 {} usunął **{}** wiadomości ✅".format(ctx.message.author.mention, len(messages)))
        logs_channel = await self.get_logs_channel(ctx.guild)
        if logs_channel:
            embed = self.bot.embed()
            embed.title = "Czyszczenie kanału"
            embed.add_field(name="🧑 Wykonane przez", value=ctx.author.mention, inline=False)
            embed.add_field(name="🔢 Ilość", value=f"{len(messages)}", inline=False)
            embed.add_field(name="🔤 Kanał", value=ctx.channel.mention, inline=False)
            await logs_channel.send(embed=embed)

    @commands.command(aliases=["ogłoszenie", "ogloszenie"], usage="<tekst>", description="Tworzy ogłoszenie")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def advert(self, ctx, *, content: str):
        embed = self.bot.embed(ctx.author)
        embed.title = "Ogłoszenie"
        embed.description = content
        message = await ctx.send(embed=embed)
        await ctx.message.delete()
        await message.add_reaction("👍")
        await message.add_reaction("❤")
        await message.add_reaction("😆")
        await message.add_reaction("😮")
        await message.add_reaction("😢")
        await message.add_reaction("😠")

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

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        logs_channel = await self.get_logs_channel(message.guild)
        if logs_channel:
            embed = self.bot.embed()
            embed.title = "Usunięta wiadomość"
            embed.add_field(name="🧑 Autor", value=message.author.mention, inline=False)
            embed.add_field(name="✍️Treść", value="```{}```".format(message.clean_content), inline=False)
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, old, new):
        if old.author.bot:
            return
        if old.content != new.content:
            logs_channel = await self.get_logs_channel(old.guild)
            if logs_channel:
                embed = self.bot.embed()
                embed.title = "Edytowana wiadomość"
                embed.add_field(name="🧑 Autor", value=old.author.mention, inline=False)
                embed.add_field(name="❎ Poprzednia treść", value="```{}```".format(old.clean_content), inline=False)
                embed.add_field(name="✅ Aktualna treść", value="```{}```".format(new.clean_content), inline=False)
                await logs_channel.send(embed=embed)

    @commands.command(description="Zbanuj użytkownika",
                      usage="@uzytkownik <powód>")
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason: str):
        await member.ban(delete_message_days=0)
        await self.save_to_event_logs(ctx.guild.id, "ban", ctx.author.id, member.id, reason)
        await ctx.send("🔨 {} **zbanował** {} z powodu `{}`".format(
            ctx.author.mention,
            member.name + "#" + member.discriminator,
            reason
        ))
        await ctx.message.delete()
        try:
            await member.send("🔨 Zostałeś zbanowany na serwerze {} przez {} z powodu `{}`".format(
                ctx.guild.name, ctx.author.mention, reason))
        except discord.Forbidden:
            pass
        logs_channel = await self.get_logs_channel(ctx.guild)
        if logs_channel:
            embed = self.bot.embed()
            embed.title = "Zbanowanie użytkownika"
            embed.add_field(name="🧑 Przez", value=ctx.author.mention, inline=False)
            embed.add_field(name="🧍 Zbanowany", value=member.mention, inline=False)
            embed.add_field(name="🔤 Powód", value=reason, inline=False)
            await logs_channel.send(embed=embed)

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
        try:
            member_name, member_discriminator = member.split('#')
        except ValueError:
            raise commands.BadArgument
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await self.save_to_event_logs(ctx.guild.id, "unban", ctx.author.id, user.id, None)
                await ctx.send("✅ {} odbanował {}".format(ctx.author.mention, member))
                await ctx.message.delete()
                logs_channel = await self.get_logs_channel(ctx.guild)
                if logs_channel:
                    embed = self.bot.embed()
                    embed.title = "Odbanowanie użytkownika"
                    embed.add_field(name="🧑 Przez", value=ctx.author.mention, inline=False)
                    embed.add_field(name="🧍 Odbanowany", value=member, inline=False)
                    await logs_channel.send(embed=embed)
                return
        await ctx.send("❌ Nie odnaleziono użytkownika o podanej nazwie.")

    @commands.command(description="Wyrzuć użytkownika", usage="@użytkownik <powód>")
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason: str):
        await member.kick(reason=reason)
        await self.save_to_event_logs(ctx.guild.id, "kick", ctx.author.id, member.id, reason)
        await ctx.send("🦶 {} wyrzucił {} z powodu {}".format(
            ctx.author.mention,
            member.name + "#" + member.discriminator,
            reason
        ))
        await ctx.message.delete()
        try:
            await member.send("🦶 Zostałeś wyrzucony z serwera {} przez {} z powodu `{}`".format(
                ctx.guild.name, ctx.author.mention, reason))
        except discord.Forbidden:
            pass
        logs_channel = await self.get_logs_channel(ctx.guild)
        if logs_channel:
            embed = self.bot.embed()
            embed.title = "Wyrzucenie użytkownika"
            embed.add_field(name="🧑 Przez", value=ctx.author.mention, inline=False)
            embed.add_field(name="🧍 Wyrzucony", value=member.mention, inline=False)
            embed.add_field(name="🔤 Powód", value=reason, inline=False)
            await logs_channel.send(embed=embed)

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
        await self.save_to_event_logs(ctx.guild.id, "mute", ctx.author.id, member.id, reason if reason else None)
        if reason:
            await ctx.send("🔇 {} wyciszył {} z powodu `{}`".format(ctx.author.mention, member.mention, reason))
            try:
                await member.send("🔇 {} wyciszył Cię na serwerze **{}** z powodu `{}`".format(ctx.author.mention, ctx.guild.name, reason))
            except discord.Forbidden:
                pass
        else:
            await ctx.send("🔇 {} wyciszył {}".format(ctx.author.mention, member.mention))
            try:
                await member.send("🔇 {} wyciszył Cię na serwerze **{}**".format(ctx.author.mention, ctx.guild.name))
            except discord.Forbidden:
                pass
        await ctx.message.delete()
        logs_channel = await self.get_logs_channel(ctx.guild)
        if logs_channel:
            embed = self.bot.embed()
            embed.title = "Wyciszenie użytkownika"
            embed.add_field(name="🧑 Przez", value=ctx.author.mention, inline=False)
            embed.add_field(name="🧍 Wyciszony", value=member.mention, inline=False)
            embed.add_field(name="🔤 Powód", value=reason, inline=False) if reason else None
            await logs_channel.send(embed=embed)

    @commands.command(description="Odcisza podanego użytkownika", aliases=["odcisz"], usage="@uzytkownik")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        mutedrole = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(mutedrole)
        await self.save_to_event_logs(ctx.guild.id, "unmute", ctx.author.id, member.id, None)
        await ctx.send("🔊 {} odciszył **{}**".format(ctx.author.mention, member.mention))
        await ctx.message.delete()
        try:
            await member.send("🔊 {} odciszył Cię na serwerze **{}**".format(ctx.author.mention, ctx.guild.name))
        except discord.Forbidden:
            pass
        logs_channel = await self.get_logs_channel(ctx.guild)
        if logs_channel:
            embed = self.bot.embed()
            embed.title = "Odciszenie użytkownika"
            embed.add_field(name="🧑 Przez", value=ctx.author.mention, inline=False)
            embed.add_field(name="🧍 Odciszony", value=member.mention, inline=False)
            await logs_channel.send(embed=embed)

    @commands.command(description="Przyznaje ostrzeżenie użytkownikowi",
                      aliases=["ostrzeżenie", "ostrzezenie"],
                      usage=["@uzytkownik <powód>"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def warn(self, ctx, member: discord.Member, *, reason):
        warning = self.bot.mongo.Warns(
            server=ctx.guild.id,
            member=member.id,
            given_by=ctx.author.id,
            reason=reason,
            date=datetime.datetime.now()
        )
        warning.save()
        await self.save_to_event_logs(ctx.guild.id, "warn", ctx.author.id, member.id, reason)
        embed = self.bot.embed(ctx.author)
        embed.title = "Ostrzeżenie"
        embed.description = "⚠️{} został ostrzeżony przez {} z powodu `{}`".format(
            member.mention, ctx.author.mention, reason)
        embed.color = discord.Color.gold()
        await ctx.send(embed=embed)
        await ctx.message.delete()
        logs_channel = await self.get_logs_channel(ctx.guild)
        if logs_channel:
            embed = self.bot.embed()
            embed.title = "Nadanie ostrzeżenie"
            embed.add_field(name="🧑 Przez", value=ctx.author.mention, inline=False)
            embed.add_field(name="🧍 Ostrzeżony", value=member.mention, inline=False)
            embed.add_field(name="🔤 Powód", value=reason, inline=False)
            await logs_channel.send(embed=embed)

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
            embed.description += "{}. `{}` od <@{}> w dniu {}\n".format(
                i, warn.reason, warn.given_by, warn.date.strftime("%d-%m-%Y %H:%M")
            )
        embed.color = discord.Color.gold()
        await ctx.send(embed=embed)
