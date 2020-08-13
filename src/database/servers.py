from mongoengine import *


class Server(document):
    _id = IntField(required=True, min_value=18, max_value=18)
    name = StringField(required=True)
