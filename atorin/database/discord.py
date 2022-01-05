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


class Logs(mongoengine.EmbeddedDocument):
    enabled = mongoengine.BooleanField(default=False)
    channel = mongoengine.IntField()


class Server(mongoengine.Document):
    id = mongoengine.IntField(primary_key=True)
    logs = mongoengine.EmbeddedDocumentField(Logs)


class Warns(mongoengine.Document):
    server = mongoengine.IntField()
    member = mongoengine.IntField()
    given_by = mongoengine.IntField()
    reason = mongoengine.StringField()
    date = mongoengine.DateTimeField(default=datetime.datetime.now())


class EventLogs(mongoengine.Document):
    server = mongoengine.IntField()
    action_by = mongoengine.IntField()
    action_on = mongoengine.IntField()
    action_name = mongoengine.StringField()
    reason = mongoengine.StringField()
    date = mongoengine.DateTimeField(default=datetime.datetime.now())


class ReactionRole(mongoengine.Document):
    message_id = mongoengine.IntField()
    roles = mongoengine.DictField()
