import geckodriver_autoinstaller

from bot import Atorin

if __name__ == '__main__':
    geckodriver_autoinstaller.install()
    bot = Atorin()
    bot.run()
