import discord
from discord.ext import commands
from discord.commands import slash_command, Option, OptionChoice
from discord.ui import Modal, InputText


from atorin.bot import Atorin
from .. import database
from ..config import config


class Admin(commands.Cog, name="🛠 Administracyjne"):
    def __init__(self, bot: Atorin):
        self.bot = bot

    async def save_to_event_logs(self, guild, action, by, on, reason):
        database.discord.EventLogs(server=guild, action_name=action, action_by=by, action_on=on, reason=reason).save()

    @slash_command(
        description="Deleting the given number of messages",
        description_localizations={"pl": "Usuwanie podanej ilości wiadomości"},
        guild_ids=config["guild_ids"],
    )
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(read_message_history=True)
    @commands.guild_only()
    async def clear(
        self,
        ctx: discord.ApplicationContext,
        limit: Option(
            int,
            name="amount",
            name_localizations={"pl": "ilość"},
            description="Number of messages to be deleted",
            description_localizations={"pl": "Liczba wiadomości do usunięcia"},
        ),
    ):
        await ctx.defer()
        if limit > 100:
            raise commands.BadArgument(
                "Nie możesz usunąć więcej niż 100 wiadomości naraz!"
                if ctx.interaction.locale == "pl"
                else "You can't remove more than 100 messages at once!"
            )
        try:
            await ctx.channel.purge(limit=limit)
        except discord.HTTPException:
            raise commands.CommandInvokeError(
                "Nie udało się usunąć wiadomości, spróbuj jeszcze raz."
                if ctx.interaction.locale == "pl"
                else "Unable to delete messages, try again."
            )
        embed = discord.Embed()
        embed.title = "Czyszczenie kanału" if ctx.interaction.guild_locale == "pl" else "Clear channel"
        embed.description = (
            f"✅ **{limit} wiadomości zostało usuniętych przez {ctx.author.mention}**"
            if ctx.interaction.guild_locale == "pl"
            else f"✅ **{limit} messages cleared by {ctx.author.mention}**"
        )
        await ctx.send(embed=embed)
        await self.save_to_event_logs(ctx.guild.id, "clear", ctx.author.id, ctx.channel.id, None)

    @slash_command(
        description="Ban user",
        description_localizations={"pl": "Zbanuj użytkownika"},
        guild_ids=config["guild_ids"],
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            discord.Member,
            name="member",
            name_localizations={"pl": "użytkownik"},
            description="Member you want to ban",
            description_localizations={"pl": "Osoba, którą chcesz zbanować"},
        ),
        reason: Option(
            str,
            name="reason",
            name_localizations={"pl": "powód"},
            description="Reason of ban",
            description_localizations={"pl": "Powód bana"},
            required=False,
        ) = "Brak",
        delete_message_days: Option(
            str,
            name="days",
            name_localizations={"pl": "dni"},
            description="Number of days worth of messages to delete from user in guild.",
            description_localizations={
                "pl": "Liczba dni z których wiadomości pochodzące od użytkownika zostaną usunięte",
            },
            choices=[
                OptionChoice("Don't delete", "0", {"pl": "Nie usuwaj"}),
                OptionChoice("Last 24 hours", "1", {"pl": "Ostatnie 24 godziny"}),
                OptionChoice("Last week", "7", {"pl": "Ostatni tydzień"}),
            ],
            required=False,
        ) = "0",
    ):
        await ctx.defer()
        await member.ban(reason=reason, delete_message_days=delete_message_days)
        await self.save_to_event_logs(ctx.guild.id, "ban", ctx.author.id, member.id, reason)
        embed = discord.Embed()
        embed.title = "Ban"
        embed.description = (
            f"🔨 {ctx.author.mention} **zbanował** {member.mention} z powodu `{reason}`"
            if ctx.interaction.guild_locale == "pl"
            else f"🔨 {ctx.author.mention} **banned** {member.mention} because of `{reason}`"
        )
        await ctx.send_followup(embed=embed)
        try:
            await member.send(
                f"🔨 Zostałeś zbanowany na serwerze {ctx.guild.name} przez {ctx.author.mention} z powodu `{reason}`"
                if ctx.interaction.guild_locale == "pl"
                else f"🔨 You are banned on {ctx.guild.name} by {ctx.author.mention} because of `{reason}`"
            )
        except discord.Forbidden:
            pass

    async def banned_searcher(ctx: discord.AutocompleteContext):
        banned_users = await ctx.interaction.guild.bans()
        return [str(entry.user) for entry in banned_users if str(entry.user).lower().startswith(ctx.value.lower())]

    @slash_command(
        description="Unban user",
        description_localizations={"pl": "Odbanuj użytkownika"},
        guild_ids=config["guild_ids"],
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unban(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            str,
            name="member",
            name_localizations={"pl": "użytkownik"},
            description="Member you want to unban",
            description_localizations={"pl": "Osoba, którą chcesz odbanować"},
            autocomplete=banned_searcher,
        ),
        reason: Option(
            str,
            name="reason",
            name_localizations={"pl": "powód"},
            description="Reason of unban",
            description_localizations={"pl": "Powód odbanowania"},
            required=False,
        ) = "Brak",
    ):
        await ctx.defer()
        banned_users = await ctx.guild.bans()
        if not banned_users:
            raise commands.BadArgument(
                "Lista zbanowanych jest pusta!" if ctx.interaction.locale == "pl" else "Banned list is empty!"
            )
        for ban_entry in banned_users:
            if str(ban_entry.user) == member:
                await ctx.guild.unban(ban_entry.user)
                await self.save_to_event_logs(ctx.guild.id, "unban", ctx.author.id, ban_entry.user.id, reason)
                embed = discord.Embed()
                embed.title = "Unban"
                embed.description = (
                    f"✅ {ctx.author.mention} **odbanował** {ban_entry.user.mention}"
                    if ctx.interaction.guild_locale == "pl"
                    else f"✅ {ctx.author.mention} **unbanned** {ban_entry.user.mention}"
                )
                await ctx.send_followup(embed=embed)

    @slash_command(
        description="Kick member",
        description_localizations={"pl": "Wyrzuć użytkownika"},
        guild_ids=config["guild_ids"],
    )
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            discord.Member,
            name="member",
            name_localizations={"pl": "użytkownik"},
            description="Member you want to kick",
            description_localizations={"pl": "Osoba, którą chcesz wyrzucić"},
        ),
        reason: Option(
            str,
            name="reason",
            name_localizations={"pl": "powód"},
            description="Reason of kick",
            description_localizations={"pl": "Powód wyrzucenia"},
            required=False,
        ) = "Brak",
    ):
        await ctx.defer()
        await member.kick(reason=reason)
        await self.save_to_event_logs(ctx.guild.id, "kick", ctx.author.id, member.id, reason)
        embed = discord.Embed()
        embed.title = "Wyrzucenie" if ctx.interaction.guild_locale == "pl" else "Kick"
        embed.description = (
            f"🦶 {ctx.author.mention} wyrzucił {member.mention} z powodu `{reason}`"
            if ctx.interaction.guild_locale == "pl"
            else f"🦶 {ctx.author.mention} kicked {member.mention} because of `{reason}`"
        )
        await ctx.send_followup(embed=embed)
        try:
            await member.send(
                f"🦶 Zostałeś **wyrzucony** z serwera **{ctx.guild.name}** przez {ctx.author.mention} z powodu `{reason}`"
                if ctx.interaction.guild_locale == "pl"
                else f"🦶 You are **kicked out** of **{ctx.guild.name}** by {ctx.author.mention} because of `{reason}`"
            )
        except discord.Forbidden:
            pass

    @slash_command(
        description="Mute user",
        description_localizations={"pl": "Wycisza użytkownika"},
        guild_ids=config["guild_ids"],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            discord.Member,
            name="member",
            name_localizations={"pl": "użytkownik"},
            description="Member you want to mute",
            description_localizations={"pl": "Osoba, którą chcesz wyciszyć"},
        ),
        reason: Option(
            str,
            name="reason",
            name_localizations={"pl": "powód"},
            description="Reason of mute",
            description_localizations={"pl": "Powód wyciszenia"},
            required=False,
        ) = "Brak",
    ):
        await ctx.defer()
        mutedrole: discord.Role | None = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mutedrole:
            mutedrole = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                if channel.permissions_for(ctx.guild.get_member(self.bot.user.id)).manage_roles:
                    await channel.set_permissions(mutedrole, speak=False, send_messages=False)
        await member.add_roles(mutedrole, reason=reason)
        await self.save_to_event_logs(ctx.guild.id, "mute", ctx.author.id, member.id, reason)
        embed = discord.Embed()
        embed.title = "Wyciszenie" if ctx.interaction.guild_locale == "pl" else "Mute"
        embed.description = (
            f"🔇 {ctx.author.mention} wyciszył {member.mention} z powodu `{reason}`"
            if ctx.interaction.guild_locale == "pl"
            else f"🔇 {ctx.author.mention} muted {member.mention} because of `{reason}`"
        )
        await ctx.send_followup(embed=embed)
        try:
            await member.send(
                f"🔇 {ctx.author.mention} wyciszył Cię na serwerze **{ctx.guild.name}** z powodu `{reason}`"
                if ctx.interaction.guild_locale == "pl"
                else f"🔇 {ctx.author.mention} muted you on **{ctx.guild.name}** because of `{reason}`"
            )
        except discord.Forbidden:
            pass

    @slash_command(
        description="Unmute user",
        description_localizations={"pl": "Odcisza użytkownika"},
        guild_ids=config["guild_ids"],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            discord.Member,
            name="member",
            name_localizations={"pl": "użytkownik"},
            description="Member you want to unmute",
            description_localizations={"pl": "Osoba, którą chcesz odciszyć"},
        ),
    ):
        await ctx.defer()
        mutedrole: discord.Role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(mutedrole)
        await self.save_to_event_logs(ctx.guild.id, "unmute", ctx.author.id, member.id, "Brak")
        embed = discord.Embed()
        embed.title = "Odciszenie" if ctx.interaction.guild_locale == "pl" else "Unmute"
        embed.description = (
            f"🔊 {ctx.author.mention} odciszył **{member.mention}**"
            if ctx.interaction.guild_locale == "pl"
            else f"🔊 {ctx.author.mention} unmuted **{member.mention}**"
        )
        await ctx.send_followup(embed=embed)
        try:
            await member.send(
                f"🔊 {ctx.author.mention} odciszył Cię na serwerze **{ctx.guild.name}**"
                if ctx.interaction.guild_locale == "pl"
                else f"🔊 {ctx.author.mention} unmuted you on **{ctx.guild.name}**"
            )
        except discord.Forbidden:
            pass

    @slash_command(
        description="Warn user",
        description_localizations={"pl": "Daje ostrzeżenie użytkownikowi"},
        guild_ids=config["guild_ids"],
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def warn(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            discord.Member,
            name="member",
            name_localizations={"pl": "użytkownik"},
            description="Member you want to warn",
            description_localizations={"pl": "Osoba, której chcesz dać ostrzeżenie"},
        ),
        reason: Option(
            str,
            name="reason",
            name_localizations={"pl": "powód"},
            description="Reason of warn",
            description_localizations={"pl": "Powód ostrzeżenia"},
            required=False,
        ) = "Brak",
    ):
        await ctx.defer()
        database.discord.Warns(
            server=ctx.guild.id,
            member=member.id,
            given_by=ctx.author.id,
            reason=reason,
        ).save()
        await self.save_to_event_logs(ctx.guild.id, "warn", ctx.author.id, member.id, reason)
        embed = discord.Embed()
        embed.title = "Ostrzeżenie" if ctx.interaction.guild_locale == "pl" else "Warn"
        embed.description = (
            f"⚠️ {member.mention} został ostrzeżony przez {ctx.author.mention} z powodu `{reason}`"
            if ctx.interaction.guild_locale == "pl"
            else f"⚠️ {member.mention} are warned by {ctx.author.mention} because of `{reason}`"
        )
        embed.color = discord.Color.gold()
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="See user's warns",
        description_localizations={"pl": "Pokazuje ostrzeżenia dane podanemu użytkownikowi"},
        guild_ids=config["guild_ids"],
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def warns(
        self,
        ctx: discord.ApplicationContext,
        member: Option(
            discord.Member,
            name="member",
            name_localizations={"pl": "użytkownik"},
            description="Member which warnings do you want to see",
            description_localizations={"pl": "Osoba, której ostrzeżenia chcesz zobaczyć"},
        ),
    ):
        await ctx.defer()
        embed = discord.Embed()
        embed.title = "Ostrzeżenia" if ctx.interaction.locale == "pl" else "Warns"
        embed.color = discord.Color.gold()
        warns: list[database.discord.Warns] = database.discord.Warns.objects(server=ctx.guild.id, member=member.id)
        if len(warns) == 0:
            embed.description = "✅ Brak ostrzeżeń" if ctx.interaction.locale == "pl" else "✅ No warnings"
        elif len(warns) == 1:
            embed.description = (
                f"{member.mention} otrzymał/a **1** ostrzeżenie\n\n"
                if ctx.interaction.locale == "pl"
                else f"{member.mention} has **1** warning\n\n"
            )
            embed.description += (
                f"1. `{warns[0].reason}` od <@{warns[0].given_by}> w dniu {warns[0].date.strftime('%d-%m-%Y %H:%M')}"
                if ctx.interaction.locale == "pl"
                else f"1. `{warns[0].reason}` from <@{warns[0].given_by}> on {warns[0].date.strftime('%d-%m-%Y %H:%M')}"
            )
        else:
            embed.description = (
                f"{member.mention} otrzymał/a **{len(warns)}** {'ostrzeżenia' if len(warns) % 10 >= 2 or len(warns) % 10 <=4 else 'ostrzeżeń'}\n\n"
                if ctx.interaction.locale == "pl"
                else f"{member.mention} has **{len(warns)}** warnings\n\n"
            )
            i = 0
            for warn in warns:
                i += 1
                embed.description += (
                    f"{i}. `{warn.reason}` od <@{warn.given_by}> w dniu {warn.date.strftime('%d-%m-%Y %H:%M')}\n"
                    if ctx.interaction.locale == "pl"
                    else f"{i}. `{warn.reason}` from <@{warn.given_by}> on {warn.date.strftime('%d-%m-%Y %H:%M')}\n"
                )
        await ctx.send_followup(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        reaction_role_message: database.discord.ReactionRole = database.discord.ReactionRole.objects(
            message_id=payload.message_id
        ).first()
        if reaction_role_message:
            roles = reaction_role_message.roles
            role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=roles[str(payload.emoji)])
            await payload.member.add_roles(role)

    @slash_command(
        description="Create announcement",
        description_localizations={"pl": "Utwórz ogłoszenie"},
        guild_ids=config["guild_ids"],
    )
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def advert(self, ctx: discord.ApplicationContext):
        class ExecModal(Modal):
            def __init__(self) -> None:
                super().__init__("Ogłoszenie" if ctx.interaction.locale == "pl" else "Announcement")
                self.add_item(
                    InputText(
                        label="Treść ogłoszenia" if ctx.interaction.locale == "pl" else "Content of announcement",
                        placeholder="Atorin jest super!"
                        if ctx.interaction.locale == "pl"
                        else "Atorin is the best bot in the entire universe!",
                        style=discord.InputTextStyle.long,
                    )
                )

            async def callback(self, interaction: discord.Interaction):
                embed = discord.Embed()
                embed.title = "Ogłoszenie" if interaction.guild_locale == "pl" else "Announcement"
                embed.description = self.children[0].value
                embed.set_thumbnail(url=str(ctx.guild.icon))
                interaction = await interaction.response.send_message(embeds=[embed])
                message = await interaction.original_message()
                await message.add_reaction("👍")
                await message.add_reaction("❤")
                await message.add_reaction("😆")
                await message.add_reaction("😮")
                await message.add_reaction("😢")
                await message.add_reaction("😠")

        modal = ExecModal()
        await ctx.interaction.response.send_modal(modal)


def setup(bot):
    bot.add_cog(Admin(bot))
