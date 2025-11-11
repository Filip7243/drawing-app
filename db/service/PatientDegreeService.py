from db.models import PatientDegree
from db.repository.PatientDegreeRepository import PatientDegreeRepository


class PatientService:
    patientRepo = PatientDegreeRepository()

# TODO: dokonczyc ta metode
    def createOrUpdatePatient(self, patientDegree: PatientDegree):
        """
        Metoda tworzy rekord edukacji pacjenta w bd jeśl ten nie istnieje,
        jeśli istnieje to i jest taki sam jak podany w parametrze to nie robi nic,
        jeśli jest inny, to znaczy, że pacjent został zbadany po raz kolejny i zdążył
        przez ten czas przejść wyżej w edukacji, np. z poziomu podstawówki na szkołę średnią,
        wówczas dodajemy
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
