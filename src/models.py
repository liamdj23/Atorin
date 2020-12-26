import mongoengine


class Logs(mongoengine.EmbeddedDocument):
    enabled = mongoengine.BooleanField()
    events = mongoengine.ListField()
    channel = mongoengine.IntField()


class Server(mongoengine.Document):
    id = mongoengine.IntField(primary_key=True)
    logs = mongoengine.EmbeddedDocumentField(Logs)


class Token(mongoengine.Document):
    name = mongoengine.StringField(primary_key=True)
    key = mongoengine.StringField()
