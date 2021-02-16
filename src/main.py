from bot import Atorin
import geckodriver_autoinstaller

if __name__ == '__main__':
    geckodriver_autoinstaller.install()
    bot = Atorin()
    bot.loop.create_task(bot.run())
    bot.loop.create_task(bot.web.start())
