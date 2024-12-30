from peewee import SqliteDatabase, Model

from .. import connection as db


class BaseModel(Model):
    class Meta:
        database: SqliteDatabase = db
