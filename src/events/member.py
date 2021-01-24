class MemberEvents:
    def __init__(self, bot):
        self.bot = bot

        @self.bot.event
        async def on_member_join(member):
            update_users_stats(self.bot.influx, member.guild.id, len(self.bot.users))
            server = self.bot.mongo.Server.objects(id=member.guild.id).first()
            if server and server.logs.enabled and "join" in server.logs.events:
                embed = await self.bot.embed()
                embed.title = "Nowy członek serwera"
                embed.description = member.name
                await bot.get_channel(server.logs.channel).send(embed=embed)

        @self.bot.event
        async def on_member_remove(member):
            update_users_stats(self.bot.influx, member.guild.id, len(self.bot.users))
            server = self.bot.mongo.Server.objects(id=member.guild.id).first()
            if server and server.logs.enabled and "leave" in server.logs.events:
                embed = await self.bot.embed()
                embed.title = "Użytkownik opuścił serwer"
                embed.description = member.name
                await bot.get_channel(server.logs.channel).send(embed=embed)


def update_users_stats(influx, server, value):
    influx.write_points([{
        "measurement": "users",
        "tags": {
            "serverId": server
        },
        "fields": {
            "value": value
        }
    }])