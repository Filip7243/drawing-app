from db.repository.PatientRepository import PatientRepository
from db.models import Patient


class PatientService:
    patientRepo = PatientRepository()

    def createOrUpdatePatient(self, patient: Patient):
        """
        Metoda tworzy rekord pacjenta w bd jeśl ten nie istnieje,
        jeśli istnieje to go aktualizuje (jeśli jakieś dane się zmieniły)
        :param patient: Dane pacjenta z formularza startowego
        """
        found_patient = self.patientRepo.get_patient_by_identity(patient.first_name, patient.last_name,
                                                                 patient.date_of_birth, patient.gender,
                                                                 patient.dominant_hand)

        print("FOUND PATIENT: ", found_patient)
        if not found_patient:
            return self.patientRepo.insert_patient(patient)
        else:
            return self.patientRepo.update_patient(patient, found_patient.id)
