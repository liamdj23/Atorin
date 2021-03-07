from aiohttp import web
import aiohttp_jinja2
from aiohttp_session import get_session


class Login(web.View):
    async def get(self):
        session = await get_session(self.request)
        discord = self.request.app["discord"]
        if "code" in self.request.rel_url.query:
            session["access_token"], session["refresh_token"] = discord.get_token(self.request.rel_url.query["code"])
            location = self.request.app.router["login"].url_for()
            raise web.HTTPFound(location=location)
        elif session.get("access_token"):
            location = self.request.app.router["servers"].url_for()
            raise web.HTTPFound(location=location)
        else:
            location = discord.get_authorize_url()
            raise web.HTTPFound(location=location)


def authenticated_only(function):
    async def decorator_authenticated_only(*args, **kwargs):
        session = await get_session(args[0].request)
        if session.get("access_token"):
            return await function(*args, **kwargs)
        else:
            location = args[0].request.app.router["login"].url_for()
            raise web.HTTPFound(location=location)
    return decorator_authenticated_only


class Servers(web.View):
    @authenticated_only
    @aiohttp_jinja2.template("servers.html")
    async def get(self):
        session = await get_session(self.request)
        discord = self.request.app["discord"]
        guilds = discord.get_guilds(session["access_token"])
        servers = []
        for server in guilds:
            if server["permissions"] == 2147483647:
                servers.append(server)
        return {
            "avatar": self.request.app["bot"].user.avatar_url,
            "data": servers,
            "user": self.request.app["discord"].get_user(session.get("access_token"))
        }


class Server(web.View):
    @authenticated_only
    @aiohttp_jinja2.template("server.html")
    async def get(self):
        server_id = self.request.match_info.get("server_id")
        if server_id:
            bot = self.request.app["bot"]
            session = await get_session(self.request)
            if bot.get_guild(int(server_id)):
                return {
                    "avatar": self.request.app["bot"].user.avatar_url,
                    "user": self.request.app["discord"].get_user(session.get("access_token"))
                }
            else:
                raise web.HTTPFound(location="/addbot")
        else:
            location = self.request.app.router["servers"].url_for()
            raise web.HTTPFound(location=location)


class Logout(web.View):
    @authenticated_only
    async def get(self):
        session = await get_session(self.request)
        session.invalidate()
        location = self.request.app.router["index"].url_for()
        raise web.HTTPFound(location=location)
