import datetime

import mongoengine


class Logs(mongoengine.EmbeddedDocument):
    enabled = mongoengine.BooleanField()
    channel = mongoengine.IntField()


class Server(mongoengine.Document):
    id = mongoengine.IntField(primary_key=True)
    logs = mongoengine.EmbeddedDocumentField(Logs)


class Token(mongoengine.Document):
    id = mongoengine.StringField(primary_key=True)
    key = mongoengine.StringField()


class Payments(mongoengine.Document):
    id = mongoengine.StringField(primary_key=True)
    user = mongoengine.IntField()
    paid = mongoengine.BooleanField(default=False)
    created = mongoengine.DateTimeField(default=datetime.datetime.utcnow())


class Premium(mongoengine.Document):
    id = mongoengine.IntField(primary_key=True)
    created = mongoengine.DateTimeField(default=datetime.datetime.utcnow())
    expire = mongoengine.DateTimeField(default=datetime.datetime.utcnow())
