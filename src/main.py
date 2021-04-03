from bot import Atorin
from pyfiglet import Figlet

f = Figlet()

if __name__ == '__main__':
    print(f.renderText("ATORIN"))
    bot = Atorin()
    print("\033[95m * Starting Atorin...")
    bot.run()
