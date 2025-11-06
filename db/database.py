from datetime import datetime

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
        # self._create_table()

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

    def _create_table(self):
        query = """
        CREATE TYPE school AS ENUM ('PODSTAWOWE', 'SREDNIE', 'WYZSZE');
        CREATE TYPE school_details AS ENUM ('KLASA1', 'KLASA2', 'KLASA3', 'KLASA4',
         'KLASA5', 'KLASA6', 'KLASA7', 'KLASA8', 'TECHNIKUM', 'LICEUM', 'LICENCJAT', 'MAGISTER', 'DOKTORAT');
        CREATE TYPE mode AS ENUM ('NORMALNY', 'UPROSZCZONY');
        CREATE TYPE hand AS ENUM ('PRAWA', 'LEWA');
        CREATE TYPE gender AS ENUM ('MEZCZYZNA', 'KOBIETA');
        
        CREATE TABLE IF NOT EXISTS examine_records (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            date_of_birth DATE,
            gender gender,
            dominant_hand hand,
            eye_impairment BOOLEAN,
            eye_description TEXT,
            education school,
            education_details school_details,
            additional_info TEXT,
            examine_reason TEXT,
            mode mode,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_examine_records_multi
            ON examine_records(first_name, last_name, date_of_birth, dominant_hand);
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            print("Tabela `examine_records` gotowa")

    def insert_record(self, data: dict):
        query = """
                INSERT INTO examine_records (first_name, last_name, date_of_birth, gender, dominant_hand,
                                             eye_impairment, eye_description, education, education_details,
                                             additional_info, examine_reason, mode, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); \
                """
        with self.conn.cursor() as cur:
            cur.execute(query, (
                data.get("first_name"),
                data.get("last_name"),
                data.get("date_of_birth").strftime("%Y-%m-%d"),
                data.get("gender"),
                data.get("dominant_hand"),
                data.get("eye_impairment"),
                data.get("eye_description"),
                data.get("education"),
                data.get("education_details"),
                data.get("additional_info"),
                data.get("examine_reason"),
                data.get("mode"),
                datetime.now()
            ))
        print("Wpis zapisany do bazy")

    def close(self):
        if self.conn:
            self.conn.close()
            print("🔌 Połączenie z bazą zamknięte")
