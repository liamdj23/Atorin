from bot import Atorin
from pyfiglet import Figlet

f = Figlet()

if __name__ == '__main__':
    bot = Atorin()
    print(f.renderText("ATORIN"), flush=True)
    print("\033[95m * Starting Atorin...", flush=True)
    bot.run()
