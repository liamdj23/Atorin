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
import mongoengine, datetime


class Payments(mongoengine.Document):
    id = mongoengine.StringField(primary_key=True)
    user = mongoengine.IntField()
    paid = mongoengine.BooleanField(default=False)
    created = mongoengine.DateTimeField(default=datetime.datetime.now())


class Premium(mongoengine.Document):
    id = mongoengine.IntField(primary_key=True)
    created = mongoengine.DateTimeField(default=datetime.datetime.now())
    expire = mongoengine.DateTimeField(default=datetime.datetime.now())
