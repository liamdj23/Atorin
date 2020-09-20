from bot import Atorin


if __name__ == '__main__':
    bot = Atorin()
    bot.loop.create_task(bot.run())
    bot.loop.create_task(bot.web.start())
