from mongoengine import *


class Token(Document):
    name = StringField(required=True)
    key = StringField(required=True)

