import mongoengine


class Token(mongoengine.Document):
    id = mongoengine.StringField(primary_key=True)
    key = mongoengine.StringField()
