import os
import threading

import requests
from flask import Flask

from dashboard.routes import home
from dashboard.routes import panel
from dashboard.routes import premium


class Dashboard(Flask):
    def __init__(self, bot):
        super(Dashboard, self).__init__(__name__)
        self.config["TEMPLATES_AUTO_RELOAD"] = True
        self.jinja_env.auto_reload = True
        self.secret_key = os.urandom(32).hex()
        self.bot = bot
        self.discord = Discord(bot.config)

        self.add_url_rule('/', view_func=home.home)
        self.add_url_rule('/commands', view_func=home.commands)
        self.add_url_rule('/login', view_func=panel.login)
        self.add_url_rule('/servers', view_func=panel.servers)
        self.add_url_rule('/server/<server_id>', view_func=panel.server)
        self.add_url_rule('/logout', view_func=panel.logout)
        self.add_url_rule('/premium', view_func=premium.premium)
        self.add_url_rule('/thanks', view_func=premium.thanks)
        self.add_url_rule('/buy', view_func=premium.buy)
        self.add_url_rule('/payments', view_func=premium.payments, methods=["POST"])
        self.add_url_rule('/sms', view_func=premium.sms, methods=["POST"])
        self.add_url_rule('/regulamin', view_func=home.terms)

    def start(self):
        host = "0.0.0.0"
        port = 8080
        threading.Thread(target=self.run, args=(host, port,)).start()


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

