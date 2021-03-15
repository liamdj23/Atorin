from flask import render_template, session, current_app, redirect, url_for, request


def login():
    discord = current_app.discord
    if request.args.get("code"):
        session["access_token"], session["refresh_token"] = discord.get_token(request.args.get("code"))
        if session.get("redirect"):
            return redirect(url_for(session["redirect"]))
        else:
            return redirect("/")
    elif session.get("access_token"):
        return redirect("/")
    else:
        return redirect(discord.get_authorize_url())


def servers():
    if session.get("access_token"):
        discord = current_app.discord
        bot = current_app.bot
        guilds = discord.get_guilds(session["access_token"])
        servers = []
        session["servers"] = []
        for server in guilds:
            if server["permissions"] == 2147483647:
                servers.append(server)
                session["servers"].append(server["id"])
        return render_template(
            "servers.html",
            avatar=bot.user.avatar_url,
            data=servers,
            user=discord.get_user(session.get("access_token"))
        )
    else:
        session["redirect"] = "servers"
        return redirect(url_for("login"))


def server(server_id, setting):
    if session.get("access_token"):
        if server_id and server_id in session["servers"]:
            bot = current_app.bot
            discord = current_app.discord
            guild = bot.get_guild(int(server_id))
            if guild:
                server_db = bot.mongo.Server.objects(id=guild.id).first()
                if not server_db:
                    server_db = bot.mongo.Server(id=guild.id, logs=bot.mongo.Logs())
                    server_db.save()
                if request.method == "GET":
                    return render_template(
                        "server.html",
                        avatar=bot.user.avatar_url,
                        user=discord.get_user(session.get("access_token")),
                        guild=guild,
                        logs=server_db.logs
                    )
                else:
                    if setting:
                        data = request.get_json()
                        if setting == "logs":
                            if "state" in data:
                                server_db.logs.enabled = bool(data["state"])
                                server_db.save()
                                if data["state"]:
                                    return "Zdarzenia zostały włączone!"
                                else:
                                    return "Zdarzenia zostały wyłączone!"
                            elif "channel" in data and len(data["channel"]) == 18:
                                if guild.get_channel(int(data["channel"])):
                                    server_db.logs.channel = int(data["channel"])
                                    server_db.save()
                                    return "Pomyślnie zmieniono kanał do wysyłania zdarzeń!"
                                else:
                                    return "Nie znaleziono podanego kanału na tym serwerze."
                            else:
                                return "Przesłano nieprawidłowe dane."
                        else:
                            return "Nie znaleziono podanego ustawienia."
                    else:
                        return "Musisz podać nazwę ustawienia."
            else:
                return redirect("/addbot")
        else:
            return redirect(url_for("servers"))
    else:
        session["redirect"] = "servers"
        return redirect(url_for("login"))


def logout():
    if session.get("access_token"):
        session.clear()
    return redirect("/")
