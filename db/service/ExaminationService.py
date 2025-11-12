from datetime import timedelta

from db.models import PreviousExaminationsDTO, PatientIdentity
from db.repository.ExaminationRepository import ExaminationRepository
from db.repository.PatientRepository import PatientRepository


class ExaminationService:
    examinationRepo = ExaminationRepository()
    patientRepo = PatientRepository()

    # TODO: pozniej tutaj zmienic wypelninaie danych na dane z bazy z failure jakl juz bedzie model
    # TODO: teraz jest na sztywno  celu demonstracji
    def get_patient_previous_examinations(self, patientIdentity: PatientIdentity) -> list[PreviousExaminationsDTO]:
        found_patient = self.patientRepo.get_patient_by_identity(patientIdentity.first_name,
                                                                 patientIdentity.last_name,
                                                                 patientIdentity.date_of_birth,
                                                                 patientIdentity.gender,
                                                                 patientIdentity.dominant_hand)
        print("FOUND PATIENT: ", found_patient)
        if not found_patient:
            return []

        return self.examinationRepo.get_previous_examinations(found_patient.id)

    def update_examination_times(self, examination_id, whole_time: timedelta, avg_time: timedelta):
        return self.examinationRepo.update_examination_times(whole_time, avg_time, examination_id)
