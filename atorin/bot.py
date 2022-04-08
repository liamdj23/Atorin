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
from discord.ext.commands import CommandError, NoPrivateMessage, MissingPermissions, BotMissingPermissions, BadArgument
import statcord
import httpx


class Atorin(discord.AutoShardedBot):
    def __init__(self, *args, **options) -> None:
        super().__init__(shard_count=2, shard_ids=[0, 1], *args, **options)
        self.config = config
        self.uptime: float = time.time()
        self.log = log
        if config["guild_ids"]:
            log.warn(f"🛂 Commands will be registered in {config['guild_ids']}")
        else:
            log.warn("🌍 Commands will be registered GLOBALLY!")
        log.info("🔌 Loading extensions...")
        for file in os.listdir("atorin/commands"):
            if file.endswith(".py") and not file == "__init__.py":
                name: str = file[:-3]
                try:
                    self.load_extension(f"atorin.commands.{name}")
                    log.info(f"✅ Loaded extension: {name}")
                except discord.NoEntryPointError:
                    log.error(f"❌ Extension {name} not loaded, because it doesn't have 'setup' function.")
                except discord.ExtensionFailed as e:
                    log.error(f"❌ Extension {e.name} failed to load. Error: {e.original}")
        log.info("✅ Extensions loaded successfully!")
        humanize.activate("pl_PL")
        self.statcord = statcord.Client(self, config["statcord"])
        self.statcord.start_loop()

    def run(self, *args: Any, **kwargs: Any) -> None:
        return super().run(self.config["token"], *args, **kwargs)

    def get_uptime(self) -> float:
        return time.time() - self.uptime

    def get_version(self) -> str:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("ascii").strip()

    async def on_application_command(self, ctx: discord.ApplicationContext) -> None:
        self.statcord.command_run(ctx)

    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: CommandError) -> None:
        embed = discord.Embed()
        embed.color = 0xFF0000
        if hasattr(error, "original"):
            if isinstance(error.original, NoPrivateMessage):
                embed.description = (
                    f"❌ **Tę komendę możesz użyć tylko na serwerze!**"
                    if ctx.interaction.locale == "pl"
                    else f"❌ **You can only use this command in the server!**"
                )
            elif isinstance(error.original, MissingPermissions):
                embed.description = (
                    f"❌ **Nie masz odpowiednich uprawnień do wykonania tej komendy. Wymagane uprawnienia: `{','.join(error.missing_perms)}`**"
                    if ctx.interaction.locale == "pl"
                    else f"❌ **You don't have permissions to use this command! Required permissions: `{','.join(error.missing_perms)}`**"
                )
            elif isinstance(error.original, BotMissingPermissions):
                embed.description = (
                    f"❌ **Atorin nie ma odpowiednich uprawnień do wykonania tej komendy. Wymagane uprawnienia: `{','.join(error.missing_perms)}`**"
                    if ctx.interaction.locale == "pl"
                    else f"❌ **Atorin does not have permissions to run this command!. Required permissions: `{','.join(error.missing_perms)}`**"
                )
            elif isinstance(error.original, BadArgument):
                embed.title = "Niepoprawny argument" if ctx.interaction.locale == "pl" else "Invalid argument"
                embed.description = f"❌ **{error.original}**"
            else:
                log.info(f"Unhandled error in {ctx.command.qualified_name}: {error.original.__class__.__name__}")
                embed.description = f"❌ **{ctx.command.qualified_name.capitalize()} :: {error.original}**"
        else:
            embed.description = f"❌ **{ctx.command.qualified_name.capitalize()} :: {error}**"
            log.error(f"❌ {ctx.command.qualified_name.capitalize()} :: {error}")
        await ctx.respond(embed=embed)

    async def on_ready(self) -> None:
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"˚ ༘✶ ⋆｡˚ ⁀➷"),
        )
        log.info("🤖 Atorin is ready!")

    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"z {len(self.guilds)} serwerami"),
        )
        # Post guild count to Top.gg
        if config["topgg"]:
            httpx.post(
                f"https://top.gg/api/bots/{self.user.id}/stats",
                headers={"Authorization": config["topgg"]},
                json={"server_count": len(self.guilds)},
            )

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"z {len(self.guilds)} serwerami"),
        )
        # Post guild count to Top.gg
        if config["topgg"]:
            httpx.post(
                f"https://top.gg/api/bots/{self.user.id}/stats",
                headers={"Authorization": config["topgg"]},
                json={"server_count": len(self.guilds)},
            )

    async def on_shard_connect(self, shard_id: int) -> None:
        log.info(f"👁  Atorin shard {shard_id} connected to Discord.")

    async def on_shard_disconnect(self, shard_id: int) -> None:
        log.warn(f"😳 Atorin shard {shard_id} disconnected from Discord!")
