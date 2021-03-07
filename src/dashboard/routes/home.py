from aiohttp import web
import aiohttp_jinja2
from aiohttp_session import get_session


class Home(web.View):
    @aiohttp_jinja2.template("home.html")
    async def get(self):
        bot = self.request.app["bot"]
        session = await get_session(self.request)
        return {"avatar": bot.user.avatar_url,
                "servers": len(bot.guilds),
                "channels": len(list(bot.get_all_channels())),
                "users": len(bot.users),
                "user": self.request.app["discord"].get_user(session.get("access_token"))
                }


class Commands(web.View):
    @aiohttp_jinja2.template("commands.html")
    async def get(self):
        bot = self.request.app["bot"]
        session = await get_session(self.request)
        return {
            "cogs": bot.cogs.items(),
            "avatar": bot.user.avatar_url,
            "user": self.request.app["discord"].get_user(session.get("access_token"))
        }
