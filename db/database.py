import psycopg2
from psycopg2.extras import RealDictCursor


class DatabaseManager:
    def __init__(self, host, port, dbname, user, password):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = None
        self._connect()
        if not self._is_migration_finished():
            self._run_init_sql()

    def _connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor
            )
            self.conn.autocommit = True
            print("Połączono z bazą PostgreSQL")
        except Exception as e:
            print(f"Błąd połączenia z bazą: {e}")
            raise

    def _is_migration_finished(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT finished FROM migration WHERE id = 1;")
                row = cur.fetchone()
                return row is not None and row['finished']
        except Exception as e:
            print(f"Error: Could not retrieve status of migration from database: {e}")
            return False

    def _run_init_sql(self):
        try:
            import os
            init_sql_path = os.path.join(os.path.dirname(__file__), "init.sql")
            with open(init_sql_path, "r", encoding="utf-8") as f:
                sql = f.read()
            with self.conn.cursor() as cur:
                cur.execute(sql)
                print("Migracja z pliku init.sql wykonana pomyślnie")
        except Exception as e:
            print(f"Błąd podczas wykonywania migracji: {e}")

    def close(self):
        if self.conn:
            self.conn.close()
            print("🔌 Połączenie z bazą zamknięte")
