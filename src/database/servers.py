from mongoengine import *


class Server(document):
    name = StringField(required=True)

