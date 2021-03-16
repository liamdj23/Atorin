from flask import render_template, session, current_app


def home():
    session["redirect"] = "home"
    bot = current_app.bot
    discord = current_app.discord
    return render_template(
        "home.html",
        avatar=bot.user.avatar_url,
        servers=len(bot.guilds),
        channels=len(list(bot.get_all_channels())),
        users=len(bot.users),
        user=discord.get_user(session.get("access_token"))
    )


def commands():
    session["redirect"] = "commands"
    bot = current_app.bot
    discord = current_app.discord
    return render_template(
        "commands.html",
        avatar=bot.user.avatar_url,
        cogs=bot.cogs.items(),
        user=discord.get_user(session.get("access_token"))
    )


def terms():
    session["redirect"] = "regulamin"
    bot = current_app.bot
    discord = current_app.discord
    return render_template(
        "terms.html",
        avatar=bot.user.avatar_url,
        user=discord.get_user(session.get("access_token"))
    )
