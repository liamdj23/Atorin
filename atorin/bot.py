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
import subprocess
from typing import *
import discord
import os
from .config import config
from .logger import log
import humanize
import time
from discord.ext.commands import (
    CommandError,
    NoPrivateMessage,
    MissingPermissions,
    BotMissingPermissions,
)


class Atorin(discord.AutoShardedBot):
    def __init__(self, *args, **options) -> None:
        super().__init__(shard_count=2, shard_ids=[0, 1], *args, **options)
        self.config = config
        self.uptime: float = time.time()
        self.log = log
        if config["guild_ids"]:
            log.warn(f"Commands will be registered in {config['guild_ids']}")
        else:
            log.warn("Commands will be registered GLOBALLY!")
        log.info("Loading extensions...")
        for file in os.listdir("atorin/commands"):
            if file.endswith(".py") and not file == "__init__.py":
                name: str = file[:-3]
                try:
                    self.load_extension(f"atorin.commands.{name}")
                    log.info(f"Loaded extension: {name}")
                except discord.NoEntryPointError:
                    log.error(
                        f"Extension {name} not loaded, because it doesn't have 'setup' function."
                    )
                except discord.ExtensionFailed as e:
                    log.error(f"Extension {e.name} failed to load. Error: {e.original}")
        log.info("Extensions loaded successfully!")
        humanize.activate("pl_PL")

    def run(self, *args: Any, **kwargs: Any) -> None:
        return super().run(self.config["token"], *args, **kwargs)

    def get_uptime(self) -> float:
        return time.time() - self.uptime

    def get_version(self) -> str:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("ascii")
            .strip()
        )

    async def on_application_command_error(
        self, ctx: discord.ApplicationContext, error: CommandError
    ):
        embed = discord.Embed()
        embed.color = 0xFF0000
        if isinstance(error.original, NoPrivateMessage):
            embed.description = f"❌ **Komendę **{ctx.command.qualified_name}** możesz użyć tylko na serwerze.**"
        elif isinstance(error.original, MissingPermissions):
            embed.description = f"❌ **Nie masz odpowiednich uprawnień do wykonania komendy **{ctx.command.qualified_name}**. Wymagane uprawnienia: `{','.join(error.missing_perms)}`**"
        elif isinstance(error.original, BotMissingPermissions):
            embed.description = f"❌ **Atorin nie ma odpowiednich uprawnień do wykonania komendy **{ctx.command.qualified_name}**. Wymagane uprawnienia: `{','.join(error.missing_perms)}`**"
        else:
            embed.description = (
                f"❌ **{ctx.command.qualified_name.capitalize()} :: {error.original}**"
            )
            log.error(f"{ctx.command.qualified_name.capitalize()} :: {error}")
        await ctx.respond(embed=embed)
