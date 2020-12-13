from aiohttp import web
import aiohttp_jinja2


class Handler(web.View):
    @aiohttp_jinja2.template("home.html")
    async def get(self):
        bot = self.request.app["bot"]
        return {"avatar": bot.user.avatar_url}
