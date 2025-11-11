from db.database_manager_singleton import get_db
from db.models import Patient, School, SchoolDetails, PatientSummaryDTO


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

    def get_patient_summary_by_id(self, patient_id):
        query = """
                SELECT p.id              AS id,
                       p.age_years       AS ageYears,
                       p.age_months      AS ageMonths,
                       p.age_days        AS ageDays,
                       p.gender          AS gender,
                       p.dominant_hand   AS dominantHand,
                       p.eye_description AS eyeDescription,
                       c.comment         AS comment
                FROM patient p
                         LEFT JOIN comments c ON p.id = c.patient_id
                WHERE p.id = %s
                """
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(
                    query,
                    (patient_id,),
                )
                row = cur.fetchone()
                if not row:
                    print(f"Brak wyników dla patient_id={patient_id}")
                    return None

                return PatientSummaryDTO(
                    id=row['id'],
                    age_years=row['ageyears'],
                    age_months=row['agemonths'],
                    age_days=row['agedays'],
                    gender=row['gender'],
                    dominant_hand=row['dominanthand'],
                    eye_description=row['eyedescription'],
                    comment=row['comment'],
                )
        except Exception as e:
            import traceback
            print("Błąd przy pobieraniu danych pacjenta!")
            print(f"Typ błędu: {type(e).__name__}")
            print("Treść błędu:", e)
            print(traceback.format_exc())
            return None

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
