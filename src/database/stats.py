from src.bot import Atorin

influx = Atorin().influx


def commands_usage(user, server, command):
    influx.write_points([{
        "measurement": "commandsUsage",
        "tags": {
            "userId": user,
            "serverId": server
        },
        "fields": {
            "command": command
        }
    }])
