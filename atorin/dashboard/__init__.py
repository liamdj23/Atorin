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
from quart import Quart, redirect, url_for, session, render_template, request
from quart_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from quart_discord.models import User, Guild
from discord.ext.commands import Cog
from .. import commands as cmds
import requests, hashlib, os
from ..config import config
from .. import database
import datetime


app = Quart(__name__)

app.secret_key = b"random bytes representing quart secret key"

app.config["DISCORD_CLIENT_ID"] = config["dashboard"]["client_id"]
app.config["DISCORD_CLIENT_SECRET"] = config["dashboard"]["client_secret"]
app.config["DISCORD_REDIRECT_URI"] = config["dashboard"]["domain"] + "/callback"
app.config["DISCORD_BOT_TOKEN"] = config["token"]

discord = DiscordOAuth2Session(app)


@app.route("/")
async def home():
    user: User = await discord.fetch_user()
    return await render_template(
        "home.html",
        servers=1234,
        channels=5678,
        users=9012,
        user=user,
    )


@app.route("/commands/")
async def commands():
    user: User = await discord.fetch_user()
    cogs: list = []
    for file in os.listdir("atorin/commands"):
        if file.endswith(".py") and not file == "__init__.py":
            name: str = file[:-3]
            cog: Cog = getattr(getattr(cmds, name), name.capitalize())
            cogs.append(cog({}))
    return await render_template(
        "commands.html",
        cogs=cogs,
        user=user,
    )


@app.route("/terms/")
async def terms():
    user: User = await discord.fetch_user()
    return await render_template(
        "terms.html",
        user=user,
    )


@app.route("/login/")
async def login():
    return await discord.create_session()


@app.route("/logout/")
async def logout():
    discord.revoke()
    return redirect(url_for(".home"))


@app.route("/callback/")
async def callback():
    await discord.callback()
    return redirect(url_for(".servers"))


@app.errorhandler(Unauthorized)
async def redirect_unauthorized(e):
    return redirect(url_for("login"))


@app.route("/servers/")
@requires_authorization
async def servers():
    user: User = await discord.fetch_user()
    guilds: list[Guild] = await discord.fetch_guilds()
    return await render_template(
        "servers.html",
        data=[guild for guild in guilds if guild.permissions.value == 2147483647],
        user=user,
    )


@app.route("/server/<server_id>/<setting>", methods=["GET", "POST"])
@requires_authorization
async def server(server_id: int, setting: str):
    if not server_id:
        return redirect(url_for(".servers"))
    user: User = await discord.fetch_user()
    try:
        guild: dict = await discord.bot_request(f"/guilds/{server_id}")
        channels: dict = await discord.bot_request(f"/guilds/{guild['id']}/channels")
    except Unauthorized:
        return redirect(url_for("/addbot"))
    server_db = database.discord.Server.objects(id=guild["id"]).first()
    if not server_db:
        server_db = database.discord.Server(id=guild["id"], logs=database.discord.Logs())
        server_db.save()
    event_logs = database.discord.EventLogs.objects(server=guild["id"]).order_by(
        "-date"
    )[:10]
    if request.method == "GET":
        return await render_template(
            "server.html",
            guild=guild,
            channels=channels,
            user=user,
            logs=server_db.logs,
            event_logs=event_logs
        )
    elif request.method == "POST":
        if not setting:
            return "Musisz podać nazwę ustawienia."
        data = await request.get_json()
        match setting:
            case "logs":
                if "state" in data:
                    server_db.logs.enabled = bool(data["state"])
                    server_db.save()
                    return "Zdarzenia zostały włączone!" if data["state"] else "Zdarzenia zostały wyłączone!"
                elif "channel" in data and len(data["channel"]) == 18:
                    if any(channel["id"] == data["channel"] for channel in channels):
                        server_db.logs.channel = int(data["channel"])
                        server_db.save()
                        return "Pomyślnie zmieniono kanał do wysyłania zdarzeń!"
                    else:
                        return "Nie znaleziono podanego kanału na tym serwerze."
                else:
                    return "Przesłano nieprawidłowe dane."
            case _:
                return "Nie znaleziono podanego ustawienia."
    


@app.route("/premium/")
async def premium():
    user: User = await discord.fetch_user()
    return await render_template(
        "premium.html",
        user=user,
    )


@app.route("/thanks/")
@requires_authorization
async def thanks():
    user: User = await discord.fetch_user()
    bot: dict = await discord.bot_request("/users/@me")
    if session.get("transactionSuccess"):
        data = {
            "username": "Atorin",
            "avatar.url": f"https://cdn.discordapp.com/avatars/{bot['id']}/{bot['avatar']}.png",
            "embeds": [
                {
                    "title": "Atorin Premium 💎",
                    "description": f"Użytkownik **{user}** zakupił usługę Atorin Premium na 30 dni! Dziękuję! ❤",
                    "color": 2555648,
                }
            ],
        }
        requests.post(config["shop"]["webhook"], json=data)
        session.pop("transactionSuccess", None)
        return await render_template(
            "thanks.html",
            user=user,
        )
    return redirect(url_for(".home"))


@app.route("/buy/")
@requires_authorization
async def buy():
    user: User = await discord.fetch_user()
    data = {
        "shopId": config["shop"]["id"],
        "price": 1.99,
        "control": user.id,
        "description": "Atorin Premium " + user.id,
        "notifyURL": config["dashboard"]["domain"] + "/payments",
        "returnUrlSuccess": config["dashboard"]["domain"] + "/thanks",
    }
    data_to_hash = config["shop"]["paybylink"] + "|"
    data_to_hash += "{}".format(data["shopId"]) + "|"
    data_to_hash += "{:.2f}".format(data["price"]) + "|"
    data_to_hash += data["control"] + "|"
    data_to_hash += data["description"] + "|"
    data_to_hash += data["notifyURL"] + "|"
    data_to_hash += data["returnUrlSuccess"]
    signature = hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()
    data["signature"] = signature
    r = requests.post("https://secure.pbl.pl/api/v1/transfer/generate", json=data)
    response = r.json()
    payment = database.premium.Payments(
        id=response["transactionId"],
        user=user.id,
        created=datetime.datetime.now(),
    )
    payment.save()
    session["transactionSuccess"] = True
    return redirect(response["url"])


@app.route("/payments/", methods=["POST"])
async def payments():
    data = await request.get_json()
    data_to_hash = config["shop"]["paybylink"] + "|"
    data_to_hash += "{}".format(data["transactionId"]) + "|"
    data_to_hash += data["control"] + "|"
    data_to_hash += data["email"] + "|"
    data_to_hash += "{:.2f}".format(data["amountPaid"]) + "|"
    data_to_hash += "{}".format(data["notificationAttempt"]) + "|"
    data_to_hash += data["paymentType"] + "|"
    data_to_hash += "{}".format(data["apiVersion"])
    signature = hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()
    if signature == data["signature"]:
        payment = database.premium.Payments.objects(id=data["transactionId"]).first()
        payment.paid = True
        payment.save()
        premium = database.premium.Premium.objects(id=payment["user"]).first()
        if not premium:
            premium = database.premium.Premium(id=payment["user"])
        premium.expire = premium.expire + datetime.timedelta(days=30)
        premium.save()
        wallet = database.economy.Wallet.objects(id=payment["user"]).first()
        if not wallet:
            wallet = database.economy.Wallet(id=payment["user"])
        wallet.balance += 10000
        wallet.save()
        return "OK", 200
    else:
        return "NOT OK", 400
