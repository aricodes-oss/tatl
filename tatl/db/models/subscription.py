from datetime import datetime
from peewee import CharField, IntegerField, DateTimeField
from .base import BaseModel


class Subscription(BaseModel):
    user_login = CharField()
    user_id = IntegerField()
    channel_id = IntegerField()

    last_stream_start = DateTimeField(null=True)
    last_game_name = CharField(null=True)
    last_thumbnail_url = CharField(null=True)
    last_notified_at = DateTimeField(default=datetime.fromtimestamp(0))
