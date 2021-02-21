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
