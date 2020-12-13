class MemberEvents:
    def __init__(self, bot):
        self.bot = bot

        @self.bot.event
        async def on_member_join(member):
            update_users_stats(self.bot.influx, member.guild.id, len(self.bot.users))

        @self.bot.event
        async def on_member_remove(member):
            update_users_stats(self.bot.influx, member.guild.id, len(self.bot.users))


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