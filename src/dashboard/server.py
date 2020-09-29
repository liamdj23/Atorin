from aiohttp import web


async def hello(request):
    return web.Response(text="Atorin Dashboard")


class Dashboard(web.Application):
    def __init__(self, *args, **kwargs):
        super(Dashboard, self).__init__(*args, **kwargs)
        self.add_routes([web.get("/", hello)])

    def start(self):
        web.run_app(self)
