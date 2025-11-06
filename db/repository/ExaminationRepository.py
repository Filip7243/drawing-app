from db.database_manager_singleton import get_db
from db.models import Examination


class ExaminationRepository:
    def __init__(self):
        self.db = get_db()

    def insert_examination(self, exam: Examination):
        query = """
                INSERT INTO examination (patient_id,
                                         degree_id,
                                         examination_mode,
                                         date,
                                         whole_time,
                                         avg_time,
                                         comment)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    exam.patient_id,
                    exam.degree_id,
                    exam.examination_mode.value,
                    exam.date,
                    exam.whole_time,
                    exam.avg_time,
                    exam.comment,
                ),
            )
            new_id = cur.fetchone()['id']
            self.db.conn.commit()
            return new_id

    def update_examination(self, exam: Examination):
        query = """
                UPDATE examination
                SET patient_id       = %s,
                    degree_id        = %s,
                    examination_mode = %s,
                    date             = %s,
                    whole_time       = %s,
                    avg_time         = %s,
                    comment          = %s
                WHERE id = %s
                RETURNING id; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    exam.patient_id,
                    exam.degree_id,
                    exam.examination_mode.value,
                    exam.date,
                    exam.whole_time,
                    exam.avg_time,
                    exam.comment,
                    exam.id,
                ),
            )
            updated = cur.fetchone()
            self.db.conn.commit()
            return updated['id'] if updated else None

    def get_examination_by_id(self, exam_id: int):
        query = """
                SELECT id,
                       patient_id,
                       degree_id,
                       examination_mode,
                       date,
                       whole_time,
                       avg_time,
                       comment
                FROM examination
                WHERE id = %s; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (exam_id,))
            row = cur.fetchone()
            if not row:
                return None

            # konwersja wyniku na model Examination
            return Examination(
                id=row['id'],
                patient_id=row['patient_id'],
                degree_id=row['degree_id'],
                examination_mode=row['examination_mode'],  # Mode zostanie przypisany w warstwie wyżej
                date=row['date'],
                whole_time=row['whole_time'],
                avg_time=row['avg_time'],
                comment=row['comment'],
            )
