from db.database_manager_singleton import get_db
from db.models import PatientDegree


class PatientDegreeRepository:
    def __init__(self):
        self.db = get_db()

    def insert_patient_degree(self, degree: PatientDegree):
        query = """
                INSERT INTO patient_degree (patient_id, degree, degree_details)
                VALUES (%s, %s, %s)
                RETURNING id; \
                """

        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    degree.patient_id,
                    degree.degree.value,  # Enum → string (School)
                    degree.degree_details.value,  # Enum → string (SchoolDetails)
                ),
            )
            new_id = cur.fetchone()['id']
            self.db.conn.commit()
            return new_id
