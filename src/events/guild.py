class GuildEvents:
    def __init__(self, bot):
        self.bot = bot

        @self.bot.event
        async def on_guild_join(guild):
            await self.bot.update_status()
            bot.mongo.Server(id=guild.id, logs=bot.mongo.Logs()).save()

        @self.bot.event
        async def on_guild_remove(guild):
            await self.bot.update_status()
