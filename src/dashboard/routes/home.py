from aiohttp import web
import aiohttp_jinja2


class Home(web.View):
    @aiohttp_jinja2.template("home.html")
    async def get(self):
        bot = self.request.app["bot"]
        return {"avatar": bot.user.avatar_url,
                "servers": len(bot.guilds),
                "channels": len(list(bot.get_all_channels())),
                "users": len(bot.users)}


class Commands(web.View):
    @aiohttp_jinja2.template("commands.html")
    async def get(self):
        bot = self.request.app["bot"]
        return {"cogs": bot.cogs.items(), "avatar": bot.user.avatar_url}
