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
        for server in guilds:
            if server["permissions"] == 2147483647:
                servers.append(server)
        return render_template(
            "servers.html",
            avatar=bot.user.avatar_url,
            data=servers,
            user=discord.get_user(session.get("access_token"))
        )
    else:
        session["redirect"] = "servers"
        return redirect(url_for("login"))


def server(server_id):
    if session.get("access_token"):
        if server_id:
            bot = current_app.bot
            discord = current_app.discord
            if bot.get_guild(int(server_id)):
                return render_template(
                    "server.html",
                    avatar=bot.user.avatar_url,
                    user=discord.get_user(session.get("access_token"))
                )
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
