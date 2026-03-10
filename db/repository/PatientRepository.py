from db.database_manager_singleton import get_db
from db.models import Patient, PatientSummaryDTO, Gender, Hand


class PatientRepository:
    def __init__(self):
        self.db = get_db()

    def insert_patient(self, patient: Patient):
        query = """
                INSERT INTO patient (first_name,
                                     last_name,
                                     date_of_birth,
                                     gender,
                                     dominant_hand)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    patient.first_name,
                    patient.last_name,
                    patient.date_of_birth,
                    patient.gender.value,
                    patient.dominant_hand.value,
                ),
            )
            new_id = cur.fetchone()['id']
            self.db.conn.commit()
            return new_id

    def update_patient(self, patient: Patient, patient_id):
        query = """
                UPDATE patient
                SET first_name    = %s,
                    last_name     = %s,
                    date_of_birth = %s,
                    gender        = %s,
                    dominant_hand = %s
                WHERE id = %s
                RETURNING id;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    patient.first_name,
                    patient.last_name,
                    patient.date_of_birth,
                    patient.gender.value,
                    patient.dominant_hand.value,
                    patient_id,  # identyfikator pacjenta do aktualizacji
                ),
            )
            updated = cur.fetchone()
            self.db.conn.commit()
            return updated['id'] if updated else None

    def get_patient_by_identity(self, first_name, last_name, date_of_birth, gender, dominant_hand):
        query = """
                SELECT id,
                       first_name,
                       last_name,
                       date_of_birth,
                       gender,
                       dominant_hand
                FROM patient
                WHERE first_name = %s
                  AND last_name = %s
                  AND date_of_birth = %s
                  AND gender = %s
                  AND dominant_hand = %s;
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
                gender=gender,
                dominant_hand=dominant_hand,
            )

    def get_patient_summary_by_id(self, patient_id):
        query = """
                SELECT p.id                     AS id,
                       p.gender                 AS gender,
                       p.dominant_hand          AS dominant_hand,
                       e.age_years              AS age_years,
                       e.age_months             AS age_months,
                       e.age_days               AS age_days,
                       e.visual_impairment      AS visual_impairment,
                       e.impairment_description AS impairment_description,
                       e.comments               AS comments
                FROM patient p
                         LEFT JOIN examination e ON p.id = e.patient_id
                WHERE p.id = %s
                ORDER BY e.date DESC
                LIMIT 1;
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
                    age_years=row['age_years'] or 0,
                    age_months=row['age_months'] or 0,
                    age_days=row['age_days'] or 0,
                    gender=Gender(row['gender']),
                    dominant_hand=Hand(row['dominant_hand']),
                    visual_impairment=row['visual_impairment'] or False,
                    impairment_description=row['impairment_description'],
                    comment=row['comments'],
                )
        except Exception as e:
            import traceback
            print("Błąd przy pobieraniu danych pacjenta!")
            print(f"Typ błędu: {type(e).__name__}")
            print("Treść błędu:", e)
            print(traceback.format_exc())
            return None

    def get_latest_patients(self, limit=30):
        query = """
                SELECT id, first_name, last_name, date_of_birth, gender, dominant_hand
                FROM patient
                ORDER BY id DESC
                LIMIT %s;
                """
        patients = []
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(query, (limit,))
                rows = cur.fetchall()
                for row in rows:
                    patients.append(Patient(
                        id=row['id'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        date_of_birth=row['date_of_birth'],
                        gender=Gender(row['gender']),
                        dominant_hand=Hand(row['dominant_hand'])
                    ))
        except Exception as e:
            print(f"Błąd przy pobieraniu ostatnich pacjentów: {e}")
        return patients