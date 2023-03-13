import datetime as _dt

import peewee as _sql

_db = _sql.SqliteDatabase("bot.sqlite3")


class User(_sql.Model):
    chat_id = _sql.CharField()

    class Meta:
        database = _db


class Todo(_sql.Model):
    task = _sql.CharField()
    is_done = _sql.BooleanField(default=False)
    date = _sql.DateTimeField(default=_dt.datetime.now)
    user = _sql.ForeignKeyField(User)

    class Meta:
        database = _db


if __name__ == "__main__":
    _db.create_tables([User, Todo])
