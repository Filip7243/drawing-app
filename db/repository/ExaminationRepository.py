from datetime import timedelta

from db.database_manager_singleton import get_db
from db.models import Examination, PreviousExaminationsDTO


class ExaminationRepository:
    def __init__(self):
        self.db = get_db()

    def insert_examination(self, exam: Examination):
        query = """
                INSERT INTO examination (patient_id,
                                         date,
                                         whole_time,
                                         avg_time,
                                         age_years,
                                         age_months,
                                         age_days,
                                         visual_impairment,
                                         impairment_description,
                                         education,
                                         education_details,
                                         comments,
                                         examination_reason,
                                         total_duration_s,
                                         test_start_ts,
                                         test_end_ts)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    exam.patient_id,
                    exam.date,
                    exam.whole_time,
                    exam.avg_time,
                    exam.age_years,
                    exam.age_months,
                    exam.age_days,
                    exam.visual_impairment,
                    exam.impairment_description,
                    exam.education.value if exam.education else None,
                    exam.education_details.value if exam.education_details else None,
                    exam.comments,
                    exam.examination_reason,
                    exam.total_duration_s,
                    exam.test_start_ts,
                    exam.test_end_ts,
                ),
            )
            new_id = cur.fetchone()['id']
            self.db.conn.commit()
            return new_id

    def update_examination(self, exam: Examination):
        query = """
                UPDATE examination
                SET patient_id             = %s,
                    date                   = %s,
                    whole_time             = %s,
                    avg_time               = %s,
                    age_years              = %s,
                    age_months             = %s,
                    age_days               = %s,
                    visual_impairment      = %s,
                    impairment_description = %s,
                    education              = %s,
                    education_details      = %s,
                    comments               = %s,
                    examination_reason     = %s,
                    total_duration_s       = %s,
                    test_start_ts          = %s,
                    test_end_ts            = %s
                WHERE id = %s
                RETURNING id;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    exam.patient_id,
                    exam.date,
                    exam.whole_time,
                    exam.avg_time,
                    exam.age_years,
                    exam.age_months,
                    exam.age_days,
                    exam.visual_impairment,
                    exam.impairment_description,
                    exam.education.value if exam.education else None,
                    exam.education_details.value if exam.education_details else None,
                    exam.comments,
                    exam.examination_reason,
                    exam.total_duration_s,
                    exam.test_start_ts,
                    exam.test_end_ts,
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
                       date,
                       whole_time,
                       avg_time,
                       age_years,
                       age_months,
                       age_days,
                       visual_impairment,
                       impairment_description,
                       education,
                       education_details,
                       comments,
                       examination_reason,
                       total_duration_s,
                       test_start_ts,
                       test_end_ts
                FROM examination
                WHERE id = %s;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (exam_id,))
            row = cur.fetchone()
            if not row:
                return None

            from db.models import School, SchoolDetails
            return Examination(
                id=row['id'],
                patient_id=row['patient_id'],
                date=row['date'],
                whole_time=row['whole_time'],
                avg_time=row['avg_time'],
                age_years=row['age_years'],
                age_months=row['age_months'],
                age_days=row['age_days'],
                visual_impairment=row['visual_impairment'],
                impairment_description=row['impairment_description'],
                education=School(row['education']) if row['education'] else None,
                education_details=SchoolDetails(row['education_details']) if row['education_details'] else None,
                comments=row['comments'],
                examination_reason=row['examination_reason'],
                total_duration_s=float(row['total_duration_s']) if row['total_duration_s'] is not None else 0.0,
                test_start_ts=float(row['test_start_ts']) if row['test_start_ts'] is not None else 0.0,
                test_end_ts=row['test_end_ts'],
            )

    def get_previous_examinations(self, patient_id) -> list[PreviousExaminationsDTO]:
        query = """
                SELECT e.id         as id,
                       e.comments   as comments,
                       e.whole_time as whole_time,
                       e.avg_time   as avg_time,
                       e.date       as date,
                       f.pominiecia,
                       f.znieksztalcenia,
                       f.perserwacje,
                       f.rotacje,
                       f.przemieszczenia,
                       f.bledy_wzglednej_wielkosci
                FROM examination e
                         JOIN patient p ON p.id = e.patient_id
                         LEFT JOIN image i ON e.id = i.examine_id
                         LEFT JOIN failure f ON i.id = f.image_id
                WHERE p.id = %s
                ORDER BY e.date DESC;
                """

        with self.db.conn.cursor() as cur:
            cur.execute(query, (patient_id,))
            rows = cur.fetchall()
            if not rows:
                return []

            results = []
            for row in rows:
                # Uwaga: Ten DTO jest uproszczony, w rzeczywistości błędy mogą pochodzić z wielu obrazów w jednym badaniu
                # Na potrzeby tego repozytorium przyjmujemy zagregowane dane lub pierwszą wpadkę.
                results.append(PreviousExaminationsDTO(
                    patient_id=patient_id,
                    examine_id=row['id'],
                    failure_mappings=0,  # Przykładowa wartość, do wyliczenia jeśli potrzebne
                    valid_mappings=0,  # Przykładowa wartość
                    avg_time=row['avg_time'] or timedelta(0),
                    whole_time=row['whole_time'] or timedelta(0),
                    pominiecia=row['pominiecia'] or 0,
                    znieksztalcenia=row['znieksztalcenia'] or 0,
                    perserwacje=row['perserwacje'] or 0,
                    rotacje=row['rotacje'] or 0,
                    przemieszczenia=row['przemieszczenia'] or 0,
                    bledy_wzglednej_wielkosci=row['bledy_wzglednej_wielkosci'] or 0,
                    result="-----",
                    comment=row['comments'],
                    examine_date=row['date']
                ))

            return results

    def update_examination_times(self, whole_time: timedelta, avg_time: timedelta, exam_id: int):
        query = """
                UPDATE examination
                SET whole_time = %s,
                    avg_time   = %s
                WHERE id = %s
                RETURNING id;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    whole_time,
                    avg_time,
                    exam_id,
                ),
            )
            updated = cur.fetchone()
            self.db.conn.commit()
            return updated['id'] if updated else None
