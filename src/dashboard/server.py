from aiohttp import web
import aiohttp_jinja2
import jinja2
import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import base64
from cryptography import fernet
import requests

from dashboard.routes import home
from dashboard.routes import panel


class Dashboard(web.Application):
    def __init__(self, bot, *args, **kwargs):
        super(Dashboard, self).__init__(*args, **kwargs)
        aiohttp_jinja2.setup(self, loader=jinja2.FileSystemLoader('dashboard/templates'))
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        aiohttp_session.setup(self, EncryptedCookieStorage(secret_key))
        self["bot"] = bot
        self["discord"] = Discord(bot.config)

        self.add_routes([
            web.get("/", home.Home, name="index"),
            web.get("/commands", home.Commands, name="commands"),
            web.get("/login", panel.Login, name="login"),
            web.get("/servers", panel.Servers, name="servers"),
            web.get("/server/{server_id}", panel.Server, name="server"),
            web.get("/logout", panel.Logout, name="logout")
        ])

    def start(self):
        web.run_app(self)


class Discord:
    def __init__(self, config):
        self.token_url = "https://discord.com/api/oauth2/token"
        self.authorize_url = "https://discord.com/api/oauth2/authorize"
        self.revoke_url = "https://discord.com/api/oauth2/token/revoke"
        self.me_url = "https://discord.com/api/users/@me"
        self.guilds_url = self.me_url + "/guilds"
        self.config = config

    def get_token(self, code):
        data = {
            "grant_type": "authorization_code",
            "client_id": self.config["discord_oauth2_id"],
            "client_secret": self.config["discord_oauth2_secret"],
            "redirect_uri": self.config["discord_oauth2_domain"] + "/login",
            "scope": "identify guilds",
            "code": code
        }
        r = requests.post(self.token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        r.raise_for_status()
        data = r.json()
        return data["access_token"], data["refresh_token"]

    def get_user(self, access_token):
        if access_token:
            r = requests.get(self.me_url, headers={"Authorization": "Bearer {}".format(access_token)})
            r.raise_for_status()
            return r.json()
        return

    def get_guilds(self, access_token):
        r = requests.get(self.guilds_url, headers={"Authorization": "Bearer {}".format(access_token)})
        r.raise_for_status()
        return r.json()

    def revoke_token(self, access_token, refresh_token):
        r = requests.post(self.revoke_url,
                          headers={"Authorization": "Bearer {}".format(access_token),
                                   "Content-Type": "application/x-www-form-urlencoded"},
                          data={"token": refresh_token})
        r.raise_for_status()
        return

    def get_authorize_url(self):
        return "https://discord.com/oauth2/authorize?client_id={}&redirect_uri={}" \
               "/login&response_type=code&scope=identify%20guilds".format(self.config["discord_oauth2_id"],
                                                                          self.config["discord_oauth2_domain"])
