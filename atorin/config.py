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
import yaml
import sys
from .logger import log


class Configuration:
    def __init__(self) -> None:
        try:
            with open("config.yml", "r") as file:
                log.info("Reading configuration file (config.yml)...")
                self.data = yaml.safe_load(file)
                log.info("Configuration loaded successfully!")
        except FileNotFoundError:
            log.critical("Configuration file not found!")
            sys.exit(1)
        except yaml.YAMLError as e:
            log.critical(f"A problem occurred with configuration file: {e}")
            sys.exit(1)

    def get(self) -> dict:
        return self.data

    def save(self) -> None:
        try:
            with open("config.yml", "w") as file:
                yaml.dump(self.data, file)
                self.data = yaml.dump(self.data)
                log.info("Configuration file saved successfully!")
        except FileNotFoundError:
            log.critical("Configuration file not found!")
            sys.exit(1)
        except yaml.YAMLError as e:
            log.critical(f"A problem occurred with configuration file: {e}")
            sys.exit(1)


config: dict = Configuration().get()
