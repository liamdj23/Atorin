class GuildEvents:
    def __init__(self, bot):
        self.bot = bot

        @self.bot.event
        async def on_guild_join(guild):
            update_guilds_stats(self.bot.influx, len(self.bot.guilds))

        @self.bot.event
        async def on_guild_remove(guild):
            update_guilds_stats(self.bot.influx, len(self.bot.guilds))


def update_guilds_stats(influx, value):
    influx.write_points([{
        "measurement": "servers",
        "tags": {
            "bot": "atorin"
        },
        "fields": {
            "value": value
        }
    }])
