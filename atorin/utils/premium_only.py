from discord.ext import commands
from .. import database


class NoPremiumUser(commands.CheckFailure):
    pass


def premium_only() -> bool:
    async def predicate(ctx: commands.Context):
        if not database.premium.Premium.objects(id=ctx.author.id).first():
            raise NoPremiumUser
        return True

    return commands.check(predicate)
