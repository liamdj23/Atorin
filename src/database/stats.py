class Stats:
    def __init__(self, db):
        self.influx = db

    def commands_usage(self, user, server, command):
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
