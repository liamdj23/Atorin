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
import sys, os
from atorin import Atorin
from atorin import log
from atorin import dashboard
from atorin import metrics
from atorin.config import config

if __name__ == "__main__":
    # os.system("cls" if sys.platform == "win32" else "clear")
    log.info("Starting Atorin...")
    bot: Atorin = Atorin()
    log.info("Starting dashboard...")
    bot.loop.create_task(dashboard.app.run_task(host="0.0.0.0", port=8080))
    if config["metrics"]["enabled"]:
        log.info("Starting metrics...")
        metrics.prom.start_http_server(config["metrics"]["port"])
    bot.run()
