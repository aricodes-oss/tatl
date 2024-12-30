from peewee import SqliteDatabase

# TODO: load location from config/environment
connection: SqliteDatabase = SqliteDatabase("data.db", pragmas={"foreign_keys": 1})
