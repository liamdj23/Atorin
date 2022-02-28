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
import os, importlib

for file in os.listdir("atorin/commands"):
    if file.endswith(".py") and not file == "__init__.py":
        name = file[:-3]
        importlib.import_module(f".commands.{name}", "atorin")
