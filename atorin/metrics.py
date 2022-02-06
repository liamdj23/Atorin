"""
```yml
    _   _             _       
   / \ | |_ ___  _ __(_)_ __  
  / _ \| __/ _ \| '__| | '_ \ 
 / ___ \ || (_) | |  | | | | |
/_/   \_\__\___/|_|  |_|_| |_|
```
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                              
Made with ❤️ by Piotr Gaździcki.

"""

import prometheus_client as prom

servers = prom.Gauge("atorin_guilds", "Number of guilds")
users = prom.Gauge("atorin_users", "Number of users")
channels = prom.Gauge("atorin_channels", "Number of channels")
shards = prom.Gauge("atorin_shards", "Number of shards")

commands_executed = prom.Gauge(
    "atorin_commands_executed", "Executed commands", ["command"]
)
commands_executed_successfully = prom.Gauge(
    "atorin_commands_executed_successfully",
    "Commands executed successfully",
    ["command"],
)
commands_executed_with_error = prom.Gauge(
    "atorin_commands_executed_with_error", "Commands executed with error", ["command"]
)

active_players = prom.Gauge("atorin_active_players", "Number of active players")
songs = prom.Gauge("atorin_songs_played", "Played songs", ["song"])
