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
    state = mongoengine.IntField(default=5)
    limit = mongoengine.IntField(default=10)


class Thirst(mongoengine.EmbeddedDocument):
    state = mongoengine.IntField(default=5)
    limit = mongoengine.IntField(default=10)


class Sleep(mongoengine.EmbeddedDocument):
    state = mongoengine.IntField(default=5)
    limit = mongoengine.IntField(default=10)
    in_bed = mongoengine.BooleanField(default=False)


class Item(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(primary_key=True)
    type = mongoengine.IntField()
    cost = mongoengine.IntField()
    description = mongoengine.StringField()
    points = mongoengine.IntField()


class Pet(mongoengine.Document):
    owner = mongoengine.IntField(primary_key=True)
    created = mongoengine.DateTimeField(default=datetime.datetime.now())
    hunger = mongoengine.EmbeddedDocumentField(Hunger, default=Hunger())
    thirst = mongoengine.EmbeddedDocumentField(Thirst, default=Thirst())
    sleep = mongoengine.EmbeddedDocumentField(Sleep, default=Sleep())
    inventory = mongoengine.EmbeddedDocumentListField(Item)
