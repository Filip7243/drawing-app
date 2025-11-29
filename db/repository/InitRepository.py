from db.database_manager_singleton import get_db


class InitRepository:
    def __init__(self):
        self.db = get_db()

    def createTypes(self):
        query = """
            CREATE TYPE school AS ENUM ('PODSTAWOWE', 'SREDNIE', 'WYZSZE');
            CREATE TYPE school_details AS ENUM ('KLASA1', 'KLASA2', 'KLASA3', 'KLASA4',
             'KLASA5', 'KLASA6', 'KLASA7', 'KLASA8', 'TECHNIKUM', 'LICEUM', 'LICENCJAT', 'MAGISTER', 'DOKTORAT');
            CREATE TYPE mode AS ENUM ('NORMALNY', 'UPROSZCZONY');
            CREATE TYPE hand AS ENUM ('PRAWA', 'LEWA');
            CREATE TYPE gender AS ENUM ('MEZCZYZNA', 'KOBIETA');
        """
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            print("Types have been created")

    def createPatientTable(self):
        query = """
                CREATE TABLE IF NOT EXISTS patient
                (
                    id              SERIAL PRIMARY KEY,
                    first_name      TEXT,
                    last_name       TEXT,
                    date_of_birth   DATE,
                    age_years       INTEGER,
                    age_months      INTEGER,
                    age_days        INTEGER,
                    gender          gender,
                    dominant_hand   hand,
                    eye_impairment  BOOLEAN,
                    eye_description TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_patient_identity
                    ON patient (first_name, last_name, date_of_birth, gender, dominant_hand);
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            print("Patient's table has been created")

    def createCommentsTable(self):
        query = """
                CREATE TABLE IF NOT EXISTS comments
                (
                    id         SERIAL PRIMARY KEY,
                    patient_id INTEGER REFERENCES patient (id) ON DELETE CASCADE,
                    comment    TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_comments_patient_id
                    ON comments (patient_id);
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            print("Comment's table has been created")

    def createPatientDegrees(self):
        query = """
                CREATE TABLE IF NOT EXISTS patient_degree
                (
                    id             SERIAL PRIMARY KEY,
                    patient_id     INTEGER REFERENCES patient (id) ON DELETE CASCADE,
                    degree         school,
                    degree_details school_details
                );
                CREATE INDEX IF NOT EXISTS idx_degree_patient_id
                    ON patient_degree (patient_id);
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            print("Patient degree's table has been created")

    def createExamineTable(self):
        query = """
                CREATE TABLE IF NOT EXISTS examination
                (
                    id               SERIAL PRIMARY KEY,
                    patient_id       INTEGER REFERENCES patient (id) ON DELETE CASCADE,
                    examination_mode mode,
                    date             DATE,
                    whole_time       INTERVAL,
                    avg_time         INTERVAL,
                    comment          TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_examination_patient_id
                    ON examination (patient_id);
                """

        with self.db.conn.cursor() as cur:
            cur.execute(query)
            print("Examination table has been created")

    def createImageTable(self):
        query = """
                CREATE TABLE IF NOT EXISTS image
                (
                    id         SERIAL PRIMARY KEY,
                    examine_id INTEGER REFERENCES examination (id) ON DELETE CASCADE,
                    content    BYTEA,
                    time       INTERVAL
                );
                CREATE INDEX IF NOT EXISTS idx_image_examine_id
                    ON image (examine_id);
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            print("Image table has been created")

    def createExamineReasonsTable(self):
        query = """
                CREATE TABLE IF NOT EXISTS afterwards_opinion
                (
                    id         SERIAL PRIMARY KEY,
                    examine_id INTEGER REFERENCES examination (id) ON DELETE CASCADE,
                    opinion     TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_reason_examine_id
                    ON afterwards_opinion (examine_id);
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            print("Examine reason's table has been created")

    def createFailureTable(self):
        query = """
                CREATE TABLE IF NOT EXISTS failure
                (
                    id                        SERIAL PRIMARY KEY,
                    examine_id                INTEGER REFERENCES examination (id) ON DELETE CASCADE,
                    pominiecia                INTEGER,
                    znieksztalcenia           INTEGER,
                    perserwacje               INTEGER,
                    rotacje                   INTEGER,
                    przemieszczenia           INTEGER,
                    bledy_wzglednej_wielkosci INTEGER
                );
                CREATE INDEX IF NOT EXISTS idx_failure_examine_id
                    ON failure (examine_id);
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            print("Failure table has been created")
