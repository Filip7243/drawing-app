from db.database_manager_singleton import get_db
from db.models import Patient, School, SchoolDetails


class PatientRepository:
    def __init__(self):
        self.db = get_db()

    def insert_patient(self, patient: Patient):
        query = """
                INSERT INTO patient (first_name,
                                     last_name,
                                     date_of_birth,
                                     age_years,
                                     age_months,
                                     age_days,
                                     gender,
                                     dominant_hand,
                                     eye_impairment,
                                     eye_description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    patient.first_name,
                    patient.last_name,
                    patient.date_of_birth,
                    patient.age_years,
                    patient.age_months,
                    patient.age_days,
                    patient.gender.value,
                    patient.dominant_hand.value,
                    patient.eye_impairment,
                    patient.eye_description,
                ),
            )
            new_id = cur.fetchone()['id']
            self.db.conn.commit()
            return new_id

    def update_patient(self, patient: Patient, patient_id):
        print("UPDATING: ", patient)
        query = """
                UPDATE patient
                SET first_name      = %s,
                    last_name       = %s,
                    date_of_birth   = %s,
                    age_years       = %s,
                    age_months      = %s,
                    age_days        = %s,
                    gender          = %s,
                    dominant_hand   = %s,
                    eye_impairment  = %s,
                    eye_description = %s
                WHERE id = %s
                RETURNING id; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    patient.first_name,
                    patient.last_name,
                    patient.date_of_birth,
                    patient.age_years,
                    patient.age_months,
                    patient.age_days,
                    patient.gender.value,
                    patient.dominant_hand.value,
                    patient.eye_impairment,
                    patient.eye_description,
                    patient_id,  # identyfikator pacjenta do aktualizacji
                ),
            )
            updated = cur.fetchone()
            print("--UPDATED--: ", updated)
            self.db.conn.commit()
            return updated['id'] if updated else None

    def get_patient_by_identity(self, first_name, last_name, date_of_birth, gender, dominant_hand):
        query = """
                SELECT id,
                       first_name,
                       last_name,
                       date_of_birth,
                       age_years,
                       age_months,
                       age_days,
                       gender,
                       dominant_hand,
                       eye_impairment,
                       eye_description
                FROM patient
                WHERE first_name = %s
                  AND last_name = %s
                  AND date_of_birth = %s
                  AND gender = %s
                  AND dominant_hand = %s; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (first_name, last_name, date_of_birth, gender.value, dominant_hand.value),
            )
            row = cur.fetchone()
            if not row:
                return None

            return Patient(
                id=row['id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                date_of_birth=row['date_of_birth'],
                age_years=row['age_years'],
                age_months=row['age_months'],
                age_days=row['age_days'],
                gender=gender,
                dominant_hand=dominant_hand,
                eye_impairment=row['eye_impairment'],
                eye_description=row['eye_description'],
            )

    def insert_patient_degree(self, patient_id, degree: School, degree_details: SchoolDetails):
        query = """
                INSERT INTO patient_degree (patient_id, degree, degree_details)
                VALUES (%s, %s, %s)
                RETURNING id; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    patient_id,
                    degree.value,
                    degree_details.value,
                ),
            )
            new_id = cur.fetchone()['id']
            self.db.conn.commit()
            return new_id
