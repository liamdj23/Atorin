from aiohttp import web
import aiohttp_jinja2
import jinja2

from dashboard.routes import home


class Dashboard(web.Application):
    def __init__(self, bot, *args, **kwargs):
        super(Dashboard, self).__init__(*args, **kwargs)
        aiohttp_jinja2.setup(self, loader=jinja2.FileSystemLoader('dashboard/templates'))
        self["bot"] = bot

        self.add_routes([
            web.get("/", home.Home),
            web.get("/commands", home.Commands)
        ])

    def start(self):
        web.run_app(self)
