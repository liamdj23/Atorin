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
from atorin import Atorin
from atorin import log
from atorin import dashboard

if __name__ == "__main__":
    log.info("🚀 Starting Atorin...")
    bot: Atorin = Atorin()
    log.info("🎛  Starting dashboard at port 8080...")
    bot.loop.create_task(dashboard.app.run_task(host="0.0.0.0", port=8080))
    bot.run()
