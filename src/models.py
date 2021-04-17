import datetime

import mongoengine


class Logs(mongoengine.EmbeddedDocument):
    enabled = mongoengine.BooleanField(default=False)
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
    created = mongoengine.DateTimeField(default=datetime.datetime.now())


class Premium(mongoengine.Document):
    id = mongoengine.IntField(primary_key=True)
    created = mongoengine.DateTimeField(default=datetime.datetime.now())
    expire = mongoengine.DateTimeField(default=datetime.datetime.now())


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
