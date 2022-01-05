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
from mongoengine import connect
from pymongo.mongo_client import MongoClient
from ..config import config
from ..logger import log
import sys
from . import premium
from . import discord

host: str = config["database"]["host"]
port: int = config["database"]["port"]
db: str = config["database"]["db"]

mongo_client: MongoClient = connect(
    db=db, host=host, port=port, serverSelectionTimeoutMS=500
)

try:
    mongo_client.admin.command("ismaster")
except Exception:
    log.critical(
        f"Can't connect to MongoDB! (mongodb://{host}:{port}/{db}) Check configuration file and try again. Shutting down..."
    )
    sys.exit(1)

log.info(f"Successfully connected to MongoDB! ({db})")
