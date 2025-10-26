from . import database

_db_instance = None


def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = database.DatabaseManager(
            host="localhost",
            port=5432,
            dbname="bvrt",
            user="postgres",
            password="admin"
        )
    return _db_instance
