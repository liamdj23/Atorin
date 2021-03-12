import datetime
import hashlib
import re

import requests
from flask import render_template, session, current_app, redirect, url_for, request, flash


def premium():
    bot = current_app.bot
    discord = current_app.discord
    return render_template(
        "premium.html",
        avatar=bot.user.avatar_url,
        user=discord.get_user(session.get("access_token"))
    )


def thanks():
    bot = current_app.bot
    discord_api = current_app.discord
    if session.get("access_token") and session.get("transactionId"):
        transaction = bot.mongo.Payments.objects(id=session["transactionId"]).first()
        if transaction and transaction.paid:
            user_api = discord_api.get_user(session["access_token"])
            data = {"username": "Atorin", "avatar_url": bot.user.avatar_url, "embeds": [{
                "title": "Atorin Premium 💎",
                "description": "Użytkownik **{}#{}** zakupił usługę Atorin Premium na 30 dni! Dziękuję! ❤".format(
                    user_api["username"], user_api["discriminator"]
                ),
                "color": 2555648
            }]}
            requests.post(bot.config["notify_channel"], json=data)
            session.pop("transactionId", None)
            return render_template(
                "thanks.html",
                avatar=bot.user.avatar_url,
                user=discord_api.get_user(session.get("access_token"))
            )
    return redirect("/")


def buy():
    if session.get("access_token"):
        bot = current_app.bot
        discord_api = current_app.discord
        user = discord_api.get_user(session["access_token"])
        data = {
            "shopId": bot.config["shopId"],
            "price": 4.99,
            "control": user["id"],
            "description": "Atorin Premium " + user["id"],
            "notifyURL": bot.config["discord_oauth2_domain"] + "/payments",
            "returnUrlSuccess": bot.config["discord_oauth2_domain"] + "/thanks"
        }
        data_to_hash = bot.config["paybylink"] + "|"
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
        payment = bot.mongo.Payments(id=response["transactionId"], user=user["id"])
        payment.save()
        session["transactionId"] = response["transactionId"]
        return redirect(response["url"])
    else:
        session["redirect"] = "buy"
        return redirect(url_for("login"))


def payments():
    bot = current_app.bot
    data = request.get_json()
    data_to_hash = bot.config["paybylink"] + "|"
    data_to_hash += "{}".format(data["transactionId"]) + "|"
    data_to_hash += data["control"] + "|"
    data_to_hash += data["email"] + "|"
    data_to_hash += "{:.2f}".format(data["amountPaid"]) + "|"
    data_to_hash += "{}".format(data["notificationAttempt"]) + "|"
    data_to_hash += data["paymentType"] + "|"
    data_to_hash += "{}".format(data["apiVersion"])
    signature = hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()
    if signature == data["signature"]:
        payment = bot.mongo.Payments.objects(id=data["transactionId"]).first()
        payment.paid = True
        premium = bot.mongo.Premium.objects(id=payment["user"]).first()
        if not premium:
            premium = bot.mongo.Premium(id=payment["user"])
        premium.expire = premium.expire + datetime.timedelta(days=30)
        premium.save()
        payment.save()
        return "OK", 200
    else:
        return "NOT OK", 400


def sms():
    error = None
    if session.get("access_token"):
        data = request.form
        if data and data["code"]:
            code = re.escape(data["code"])
            if re.match("^[A-Za-z0-9]{8}$", code):
                discord_api = current_app.discord
                user = discord_api.get_user(session["access_token"])
                bot = current_app.bot
                r = requests.get("https://www.paybylink.pl/api/v2/index.php", params={
                    "userid": bot.config["sms_userid"],
                    "serviceid": bot.config["sms_serviceid"],
                    "code": code,
                    "number": 76480
                })
                json = r.json()
                if "error" in json:
                    error = json["error"]["message"]
                elif json["data"]["status"] == 1:
                    premium = bot.mongo.Premium.objects(id=user["id"]).first()
                    if not premium:
                        premium = bot.mongo.Premium(id=user["id"])
                    premium.expire = premium.expire + datetime.timedelta(days=30)
                    premium.save()
                    return redirect(url_for("thanks"))
                else:
                    error = "Podany kod został już użyty!"
            else:
                error = "Podany kod jest nieprawidłowy!"
        else:
            error = "Musisz podać kod zwrotny z SMSa!"
    else:
        error = "Musisz być zalogowany!"
    flash(error)
    return redirect(url_for("premium"))
