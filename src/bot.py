import mongoengine
from influxdb import InfluxDBClient
from discord.ext import commands
import discord
from datetime import datetime

from cogs.fun import Fun
from cogs.admin import Admin
from cogs.info import Info
from cogs.games import Games

from settings import Settings

from logger import logger
import models
import utils

from dashboard.server import Dashboard

from events.guild import GuildEvents


class Atorin(commands.Bot):
    def __init__(self, **kwargs):
        intents = discord.Intents.default()
        intents.members = False
        super(Atorin, self).__init__(command_prefix="&", help_command=None, intents=intents, **kwargs)
        self.settings = Settings()
        mongoengine.connect('atorin')
        self.mongo = models
        self.influx = InfluxDBClient(database="atorin")
        self.influx.create_database("atorin")
        self.influx.switch_database("atorin")
        self.log = logger
        self.utils = utils
        self.web = Dashboard(self)
        self.guild_events = GuildEvents(self)
        self.add_cog(Fun(self))
        self.add_cog(Admin(self))
        self.add_cog(Info(self))
        self.add_cog(Games(self))

        @self.event
        async def on_message(message):
            ctx = await self.get_context(message)
            if ctx.author.bot and ctx.author.id == 742076835549937805:
                pass
            elif ctx.author.bot:
                return
            if ctx.command:
                await self.invoke(ctx)
                self.stats_commands_usage(ctx.author.id, ctx.guild.id, ctx.command.name)

        @self.event
        async def on_connect():
            self.log.info("Successfully connected to Discord API.")

        @self.event
        async def on_ready():
            self.log.info("Atorin is ready.")
            await self.update_status()

    async def embed(self):
        embed = discord.Embed()
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text="Atorin", icon_url=str(self.user.avatar_url))
        embed.colour = discord.Colour(0xc4c3eb)
        return embed

    def stats_commands_usage(self, user, server, command):
        self.influx.write_points([{
            "measurement": "commandsUsage",
            "tags": {
                "userId": user,
                "serverId": server
            },
            "fields": {
                "command": command
            }
        }])

    def avatar(self):
        return self.avatar()

    async def update_status(self):
        await self.change_presence(activity=discord.Game(name="Dołącz do serwera Discord! Link w &bot".format(len(self.guilds))))

    async def run(self, *args, **kwargs):
        await super(Atorin, self).start(self.settings.main["token"])

