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


class Hunger(mongoengine.EmbeddedDocument):
    state = mongoengine.IntField(default=75)
    limit = mongoengine.IntField(default=100)


class Thirst(mongoengine.EmbeddedDocument):
    state = mongoengine.IntField(default=75)
    limit = mongoengine.IntField(default=100)


class Sleep(mongoengine.EmbeddedDocument):
    state = mongoengine.IntField(default=100)
    limit = mongoengine.IntField(default=100)
    in_bed = mongoengine.BooleanField(default=False)


class Pet(mongoengine.Document):
    owner = mongoengine.IntField(primary_key=True)
    created = mongoengine.DateTimeField(default=datetime.datetime.now())
    hunger = mongoengine.EmbeddedDocumentField(Hunger, default=Hunger())
    thirst = mongoengine.EmbeddedDocumentField(Thirst, default=Thirst())
    sleep = mongoengine.EmbeddedDocumentField(Sleep, default=Sleep())
    foods = mongoengine.DictField()
    drinks = mongoengine.DictField()
    wallet = mongoengine.IntField(default=100)
    daily = mongoengine.DateTimeField()
