from io import BytesIO
from urllib.parse import quote

import aiohttp
import discord
import psutil
from discord.ext import commands

from utils import get_weather_emoji, progress_bar, convert_size


class Info(commands.Cog, name="ℹ Informacje"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Zdjęcie profilowe użytkownika\n\nPrzykład użycia:\n&avatar\n&avatar @Atorin")
    async def avatar(self, ctx, *, user: discord.User = None):
        if not user:
            user = ctx.author
        avatar = await user.avatar_url.read()
        await ctx.send(file=discord.File(BytesIO(avatar), filename=user.name + ".png"))

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&avatar @użytkownik`")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Nie znaleziono użytkownika o podanej nazwie.")
            return
        if isinstance(error, discord.HTTPException):
            await ctx.send("❌ Wystąpił błąd przy pobieraniu avatara, spróbuj ponownie.")
            return
        self.bot.log.error(error)

    @commands.command(description="Wpisz aby zaprosić Atorina na swój serwer lub uzyskać wsparcie")
    async def invite(self, ctx):
        await ctx.send("🔹 Dodaj Atorina na swój serwer, korzystając z tego linku: https://liamdj23.ovh/addbot\n"
                       + "🔸 Dołącz do serwera support: https://discord.gg/Ygr5wAZbsZ")

    @commands.command(description="Informacje o serwerze")
    @commands.guild_only()
    async def server(self, ctx):
        guild = ctx.guild
        embed = self.bot.embed(ctx.author)
        embed.title = "Informacje o " + guild.name
        embed.add_field(name="🆔 ID", value=guild.id)
        embed.add_field(name="🌍 Region", value=guild.region)
        embed.add_field(name="💬 Liczba kanałów", value=len(guild.channels))
        embed.add_field(name="👥 Liczba członków", value=guild.member_count)
        embed.add_field(name="👶 Data utworzenia", value=guild.created_at.replace(microsecond=0))
        embed.set_thumbnail(url=guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(description="Informacje o użytkowniku\n\nPrzykład użycia:\n&user\n&user @Atorin")
    @commands.guild_only()
    async def user(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = self.bot.embed(ctx.author)
        embed.title = "Informacje o " + member.name + "#" + member.discriminator
        embed.add_field(name="🆔 ID", value=member.id)
        if member.nick:
            embed.add_field(name="🎭 Pseudonim", value=member.nick)
        embed.add_field(name="👶 Data utworzenia konta", value=member.created_at.replace(microsecond=0), inline=False)
        embed.add_field(name="🤝 Data dołączenia", value=member.joined_at.replace(microsecond=0))
        roles = ", ".join(role.mention for role in member.roles)
        embed.add_field(name="🏅 Role", value=roles)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

    @user.error
    async def user_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tej komendy można użyć tylko na serwerze!")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Nie znaleziono użytkownika na tym serwerze!")
            return
        self.bot.log.error(error)

    @server.error
    async def server_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Tej komendy można użyć tylko na serwerze!")
            return
        self.bot.log.error(error)

    @commands.command(aliases=["pogoda"],
                      description="Wpisz aby otrzymać aktualną pogodę w Twojej miejscowości\n\nPrzykład użycia: &pogoda Kraków",
                      usage="<miejscowość>")
    async def weather(self, ctx, *, city: str):
        token = self.bot.config["weather"]
        async with aiohttp.ClientSession() as session:
            async with session.get('http://api.openweathermap.org/data/2.5/weather?appid={0}&units=metric&lang=pl&q={1}'
                                   .format(token, quote(city))) as r:
                if r.status == 200:
                    data = await r.json()
                    embed = self.bot.embed(ctx.author)
                    embed.title = "Pogoda w " + data["name"]
                    emoji = get_weather_emoji(data["weather"][0]["id"])
                    embed.add_field(name=emoji + " Pogoda", value=data["weather"][0]["description"])
                    embed.add_field(name="🌡️ Temperatura", value=str(data["main"]["temp"]) + "°C", inline=False)
                    embed.add_field(name="🎈 Ciśnienie", value=str(data["main"]["pressure"]) + "hPa")
                    embed.add_field(name="💧 Wilgotność", value=str(data["main"]["humidity"]) + "%")
                    embed.add_field(name="💨 Wiatr", value=str(data["wind"]["speed"]) + "m/s")
                    await ctx.send(embed=embed)
                elif r.status == 404:
                    raise commands.BadArgument
                else:
                    raise commands.CommandError

    @weather.error
    async def weather_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Poprawne użycie: `&pogoda <miejscowość>`")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Nie znaleziono podanej miejscowości.")
            return
        if isinstance(error, commands.CommandError):
            await ctx.send("❌ Wystąpił błąd, spróbuj ponownie później.")
            return
        self.bot.log.error(error)

    @commands.command(description="Wpisz aby otrzymać informacje o Atorinie")
    async def bot(self, ctx):
        embed = self.bot.embed(ctx.author)
        embed.title = "Informacje o Atorinie"
        embed.add_field(name="🌐 Liczba serwerów", value=len(self.bot.guilds))
        embed.add_field(name="👨‍💻 Autor", value="liamdj23#9081")
        embed.add_field(name="🎭 Discord", value="https://discord.gg/Ygr5wAZbsZ", inline=False)
        ram = psutil.virtual_memory()
        total_ram = convert_size(ram.total)
        used_ram = convert_size(ram.used)
        disk = psutil.disk_usage('/')
        total_disk = convert_size(disk.total)
        used_disk = convert_size(disk.used)
        embed.add_field(name="🖥 Użycie zasobów", inline=False, value="```css\n{0}\n{1}\n{2}```".format(
            progress_bar(int(psutil.cpu_percent()), "CPU"),
            progress_bar(int((ram.used / ram.total) * 100), "RAM {}/{}".format(used_ram, total_ram)),
            progress_bar(int(disk.percent), "Dysk {}/{}".format(used_disk, total_disk)))
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["pomoc", "komendy", "?"], description="Lista komend AtorinBot")
    async def help(self, ctx, arg=None):
        embed = self.bot.embed(ctx.author)
        embed.title = "Lista komend AtorinBot"
        all_commands = {}
        for command in self.bot.commands:
            all_commands[command.name] = command
            for alias in command.aliases:
                all_commands[alias] = command
        if not arg:
            embed.description = "💬 Oznacz Atorina na początku wiadmości aby z nim porozmawiać! (beta)\n" \
                                "⤴ Przy zakupie usługi w hostingu lvlup.pro," \
                                " skorzystaj z kodu `liamdj23.ovh` aby otrzymać 10% zniżki!\n" \
                                "💌 Dołącz do serwera aby być na bieżąco z nowościami: http://liamdj23.ovh/discord\n\n" \
                                "🔠 Liczba komend: {}" \
                                "\n❓ Aby uzyskać więcej informacji o komendzie wpisz &help komenda" \
                                " np. `&help shiba`".format(len(self.bot.commands))
            for name, cog in self.bot.cogs.items():
                if name != "StatcordPost":
                    cog_commands = ", ".join([c.name for c in cog.get_commands()])
                    embed.add_field(name=name, value="```{}```".format(cog_commands), inline=False)
            await ctx.send(embed=embed)
        elif arg in all_commands:
            cmd = all_commands[arg]
            if cmd.usage:
                embed.add_field(name="▶ Komenda", value="```{} {}```".format(cmd.name, cmd.usage), inline=False)
            else:
                embed.add_field(name="▶ Komenda", value="```{}```".format(cmd.name), inline=False)
            if cmd.aliases:
                embed.add_field(name="🔠 Aliasy", value="```{}```".format(", ".join(cmd.aliases)), inline=False)
            embed.add_field(name="💬 Opis", value="```{}```".format(cmd.description))
            await ctx.send(embed=embed)

    @commands.command(description="Kup lub sprawdź status Atorin Premium", aliases=["donate"])
    async def premium(self, ctx):
        embed = self.bot.embed(ctx.author)
        data = self.bot.mongo.Premium.objects(id=ctx.author.id).first()
        embed.title = "Atorin Premium"
        embed.color = discord.Color(0x07fc03)
        if data:
            embed.description = "💎 {}, Twoje premium jest **aktywne** i jest ważne do **{}**".format(
                ctx.author.mention, data.expire.strftime("%d/%m/%Y %H:%M")
            )
        else:
            embed.description = "💎 Wesprzyj bota kupując Atorin Premium, w zamian otrzymasz dostęp do eksluzywnych" \
                                " funkcji. Więcej informacji znajdziesz [na stronie bota](https://liamdj23.ovh/premium)."
        await ctx.send(embed=embed)
