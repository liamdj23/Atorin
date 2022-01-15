import discord
from discord.ext import commands
from discord.commands import slash_command, Option, OptionChoice

from atorin.bot import Atorin
from .. import database


class Admin(commands.Cog, name="🛠 Administracyjne"):
    def __init__(self, bot: Atorin):
        self.bot = bot

    async def save_to_event_logs(self, guild, action, by, on, reason):
        database.discord.EventLogs(
            server=guild, action_name=action, action_by=by, action_on=on, reason=reason
        ).save()

    @slash_command(description="Czyszczenie kanału", guild_ids=[408960275933429760])
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(read_message_history=True)
    @commands.guild_only()
    async def clear(
        self,
        ctx: discord.ApplicationContext,
        limit: Option(int, "Liczba wiadomości do usunięcia"),
    ):
        await ctx.defer()
        try:
            async for message in ctx.channel.history(limit=limit):
                try:
                    await message.delete()
                except discord.NotFound:
                    pass
                except discord.HTTPException:
                    pass
        except discord.HTTPException:
            raise commands.CommandInvokeError(
                "Nie udało się pobrać historii wiadomości."
            )

        await self.save_to_event_logs(
            ctx.guild.id, "clear", ctx.author.id, ctx.channel.id, None
        )

    @slash_command(description="Tworzy ogłoszenie", guild_ids=[408960275933429760])
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def advert(
        self, ctx: discord.ApplicationContext, content: Option(str, "Treść ogłoszenia")
    ):
        embed = discord.Embed()
        embed.title = "Ogłoszenie"
        embed.description = content
        embed.set_thumbnail(url=str(ctx.guild.icon))
        message = await ctx.respond(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("❤")
        await message.add_reaction("😆")
        await message.add_reaction("😮")
        await message.add_reaction("😢")
        await message.add_reaction("😠")

    @slash_command(
        description="Zbanuj użytkownika",
        guild_ids=[408960275933429760, 927690374305157260],
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(
        self,
        ctx: discord.ApplicationContext,
        member: Option(discord.Member, "Osoba którą chcesz zbanować"),
        reason: Option(str, "Powód bana", required=False) = "Brak",
        delete_message_days: Option(
            str,
            "Usuń historię wiadomości",
            choices=[
                OptionChoice("Nie usuwaj", "0"),
                OptionChoice("Ostatnie 24 godziny", "1"),
                OptionChoice("Ostatni tydzień", "7"),
            ],
            required=False,
        ) = "0",
    ):
        await member.ban(reason=reason, delete_message_days=delete_message_days)
        await self.save_to_event_logs(
            ctx.guild.id, "ban", ctx.author.id, member.id, reason
        )
        embed = discord.Embed()
        embed.title = "Ban"
        embed.description = (
            f"🔨 {ctx.author.mention} **zbanował** {member.mention} z powodu `{reason}`"
        )
        await ctx.respond(embed=embed)
        try:
            await member.send(
                f"🔨 Zostałeś zbanowany na serwerze {ctx.guild.name} przez {ctx.author.mention} z powodu `{reason}`"
            )
        except discord.Forbidden:
            pass

    async def banned_searcher(ctx: discord.AutocompleteContext):
        banned_users = await ctx.interaction.guild.bans()
        return [
            str(entry.user)
            for entry in banned_users
            if str(entry.user).lower().startswith(ctx.value.lower())
        ]

    @slash_command(
        description="Odbanuj użytkownika",
        guild_ids=[408960275933429760, 927690374305157260],
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unban(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            str, "Osoba którą chcesz odbanować", autocomplete=banned_searcher
        ),
        reason: Option(str, "Powód odbanowania", required=False) = "Brak",
    ):
        banned_users = await ctx.guild.bans()
        if not banned_users:
            raise commands.BadArgument("Lista zbanowanych jest pusta!")
        for ban_entry in banned_users:
            if str(ban_entry.user) == member:
                await ctx.guild.unban(ban_entry.user)
                await self.save_to_event_logs(
                    ctx.guild.id, "unban", ctx.author.id, ban_entry.user.id, reason
                )
                embed = discord.Embed()
                embed.title = "Unban"
                embed.description = (
                    f"✅ {ctx.author.mention} **odbanował** {ban_entry.user.mention}"
                )
                await ctx.respond(embed=embed)

    @slash_command(
        description="Wyrzuć użytkownika",
        guild_ids=[408960275933429760, 927690374305157260],
    )
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(
        self,
        ctx: discord.ApplicationContext,
        member: Option(discord.Member, "Osoba którą chcesz wyrzucić"),
        reason: Option(str, "Powód wyrzucenia", required=False) = "Brak",
    ):
        await member.kick(reason=reason)
        await self.save_to_event_logs(
            ctx.guild.id, "kick", ctx.author.id, member.id, reason
        )
        embed = discord.Embed()
        embed.title = "Wyrzucenie"
        embed.description = (
            f"🦶 {ctx.author.mention} wyrzucił {member.mention} z powodu `{reason}`"
        )
        await ctx.respond(embed=embed)
        try:
            await member.send(
                f"🦶 Zostałeś **wyrzucony** z serwera **{ctx.guild.name}** przez {ctx.author.mention} z powodu `{reason}`"
            )
        except discord.Forbidden:
            pass

    @slash_command(
        description="Wycisza użytkownika",
        guild_ids=[408960275933429760, 927690374305157260],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(
        self,
        ctx: discord.ApplicationContext,
        member: Option(discord.Member, "Wybierz osobę, którą chcesz wyciszyć"),
        reason: Option(str, "Powód wyciszenia", required=False) = "Brak",
    ):
        mutedrole: discord.Role | None = discord.utils.get(
            ctx.guild.roles, name="Muted"
        )
        if not mutedrole:
            mutedrole = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                if channel.permissions_for(
                    ctx.guild.get_member(self.bot.user.id)
                ).manage_roles:
                    await channel.set_permissions(
                        mutedrole, speak=False, send_messages=False
                    )
        await member.add_roles(mutedrole, reason=reason)
        await self.save_to_event_logs(
            ctx.guild.id, "mute", ctx.author.id, member.id, reason
        )
        embed = discord.Embed()
        embed.title = "Wyciszenie"
        embed.description = (
            f"🔇 {ctx.author.mention} wyciszył {member.mention} z powodu `{reason}`"
        )
        await ctx.respond(embed=embed)
        try:
            await member.send(
                f"🔇 {ctx.author.mention} wyciszył Cię na serwerze **{ctx.guild.name}** z powodu `{reason}`"
            )
        except discord.Forbidden:
            pass

    @slash_command(
        description="Odcisza użytkownika",
        guild_ids=[408960275933429760, 927690374305157260],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(
        self,
        ctx: discord.ApplicationContext,
        member: Option(discord.Member, "Osoba, którą chcesz odciszyć"),
    ):
        mutedrole: discord.Role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(mutedrole)
        await self.save_to_event_logs(
            ctx.guild.id, "unmute", ctx.author.id, member.id, "Brak"
        )
        embed = discord.Embed()
        embed.title = "Odciszenie"
        embed.description = f"🔊 {ctx.author.mention} odciszył **{member.mention}**"
        await ctx.respond(embed=embed)
        try:
            await member.send(
                f"🔊 {ctx.author.mention} odciszył Cię na serwerze **{ctx.guild.name}**"
            )
        except discord.Forbidden:
            pass

    @slash_command(
        description="Daje ostrzeżenie użytkownikowi",
        guild_ids=[408960275933429760, 927690374305157260],
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def warn(
        self,
        ctx: discord.ApplicationContext,
        member: Option(discord.Member, "Osoba, której chcesz dać ostrzeżenie"),
        reason: Option(str, "Powód ostrzeżenia", required=False) = "Brak",
    ):
        database.discord.Warns(
            server=ctx.guild.id,
            member=member.id,
            given_by=ctx.author.id,
            reason=reason,
        ).save()
        await self.save_to_event_logs(
            ctx.guild.id, "warn", ctx.author.id, member.id, reason
        )
        embed = discord.Embed()
        embed.title = "Ostrzeżenie"
        embed.description = f"⚠️ {member.mention} został ostrzeżony przez {ctx.author.mention} z powodu `{reason}`"
        embed.color = discord.Color.gold()
        await ctx.respond(embed=embed)

    @slash_command(
        description="Pokazuje ostrzeżenia dane podanemu użytkownikowi",
        guild_ids=[408960275933429760, 927690374305157260],
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def warns(
        self,
        ctx: discord.ApplicationContext,
        member: Option(discord.Member, "Osoba, której ostrzeżenia chcesz wyświetlić"),
    ):
        embed = discord.Embed()
        embed.title = "Ostrzeżenia"
        embed.color = discord.Color.gold()
        warns: list[database.discord.Warns] = database.discord.Warns.objects(
            server=ctx.guild.id, member=member.id
        )
        if len(warns) == 0:
            embed.description = "✅ Brak ostrzeżeń"
        elif len(warns) == 1:
            embed.description = f"{member.mention} otrzymał/a **1** ostrzeżenie\n\n"
            embed.description += f"1. `{warns[0].reason}` od <@{warns[0].given_by}> w dniu {warns[0].date.strftime('%d-%m-%Y %H:%M')}"
        else:
            embed.description = f"{member.mention} otrzymał/a **{len(warns)}** {'ostrzeżenia' if len(warns) % 10 >= 2 or len(warns) % 10 <=4 else 'ostrzeżeń'}\n\n"
            i = 0
            for warn in warns:
                i += 1
                embed.description += f"{i}. `{warn.reason}` od <@{warn.given_by}> w dniu {warn.date.strftime('%d-%m-%Y %H:%M')}\n"
        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        reaction_role_message: database.discord.ReactionRole = (
            database.discord.ReactionRole.objects(message_id=payload.message_id).first()
        )
        if reaction_role_message:
            roles = reaction_role_message.roles
            role = discord.utils.get(
                self.bot.get_guild(payload.guild_id).roles, id=roles[str(payload.emoji)]
            )
            await payload.member.add_roles(role)


def setup(bot):
    bot.add_cog(Admin(bot))
