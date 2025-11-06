from datetime import date

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QMessageBox

from components.StyledButton import StyledButton
from components.StyledCheckBox import StyledCheckBox
from components.StyledDropdown import StyledDropdown
from components.StyledTextArea import StyledTextArea
from components.StyledTextInput import StyledTextInput
from db.repository.CommentRepository import CommentRepository
from db.repository.ExaminationRepository import ExaminationRepository
from db.repository.AfterwardsOpinionRepository import ExamineReasonRepository
from db.repository.PatientDegreeRepository import PatientDegreeRepository
from db.service.PatientService import PatientService
from db.models import Patient, Gender, Hand, Examination, Mode, PatientDegree, School, SchoolDetails, Comment, \
    AfterwardsOpinion, TestMetaData


def calculate_age(birth_date: date):
    today = date.today()

    years = today.year - birth_date.year
    months = today.month - birth_date.month
    days = today.day - birth_date.day

    if days < 0:
        months -= 1
        previous_month = (today.month - 1) or 12
        previous_year = today.year if today.month > 1 else today.year - 1
        days_in_prev_month = (
                date(previous_year, previous_month + 1, 1) - date(previous_year, previous_month, 1)).days
        days += days_in_prev_month

    if months < 0:
        years -= 1
        months += 12

    return years, months, days


class MainForm(QWidget):
    startRequested = pyqtSignal()
    patientService = PatientService()
    examinationRepository = ExaminationRepository()
    patientDegreeRepository = PatientDegreeRepository()
    commentRepository = CommentRepository()
    examineReasonRepository = ExamineReasonRepository()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.test_meta_data = None
        layout = QGridLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 8, 8, 8)

        self.first_name = StyledTextInput("Imię", placeholder="Imię", required=True)
        self.last_name = StyledTextInput("Nazwisko", placeholder="Nazwisko", required=True)
        self.date_of_birth = StyledTextInput("Data urodzenia", placeholder="Data urodzenia", is_date=True,
                                             required=True)

        name_layout = QHBoxLayout()
        name_layout.setSpacing(2)
        name_layout.addWidget(self.first_name)
        name_layout.addWidget(self.last_name)

        name_layout.setStretch(0, 1)
        name_layout.setStretch(1, 1)

        layout.addLayout(name_layout, 0, 0)
        layout.addWidget(self.date_of_birth, 0, 1)

        self.gender_radios = StyledCheckBox("Płeć", ['Mężczyzna', 'Kobieta'], is_radio=True, required=True)
        self.hands_radios = StyledCheckBox("Ręka dominująca", ['Prawa', 'Lewa'], is_radio=True, required=True)

        layout.addWidget(self.gender_radios, 1, 0)
        layout.addWidget(self.hands_radios, 1, 1)

        self.eyes_radios = StyledCheckBox("Wada wzroku", ['Tak', 'Nie'], is_radio=True, required=True)
        self.eyes_description = StyledTextArea("Opis wady")
        self.eyes_description.setFixedHeight(self.eyes_radios.sizeHint().height())

        layout.addWidget(self.eyes_radios, 2, 0, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.eyes_description, 2, 1)

        dropdown_row = QHBoxLayout()
        dropdown_row.setSpacing(50)

        # pierwszy dropdown — zawsze widoczny
        self.education_dropdown = StyledDropdown(
            label_text="Wykształcenie",
            options=list(School),
            placeholder="Wybierz poziom wykształcenia...",
            on_select=self.handle_education_select,
            required=True
        )
        dropdown_row.addWidget(self.education_dropdown)

        # drugi dropdown — ukryty na start
        self.details_dropdown = StyledDropdown(
            label_text="Szczegóły",
            placeholder="Wybierz szczegóły...",
            is_hidden=True,
            required=True
        )
        dropdown_row.addWidget(self.details_dropdown)

        layout.addLayout(dropdown_row, 3, 0, 1, 2)

        self.additional_info = StyledTextArea("Uwagi")
        self.additional_info.setFixedHeight(120)

        layout.addWidget(self.additional_info, 4, 0, 1, 2)

        self.examine_reason = StyledTextArea("Powód badania")
        self.examine_reason.setFixedHeight(100)

        layout.addWidget(self.examine_reason, 5, 0, 1, 2)

        self.mode_radios = StyledCheckBox("Tryb testu", ['Normalny', 'Uproszczony'], is_radio=True, required=True)

        layout.addWidget(self.mode_radios, 6, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # pushuje przyciski w prawo

        start_btn = StyledButton("Rozpocznij test", color="#89c057")
        start_btn.clicked.connect(self.on_start_btn_click)
        latest_examine_btn = StyledButton("Poprzednie badania", color="#EEB14C")
        latest_examine_btn.setDisabled(True)

        button_layout.addWidget(latest_examine_btn)
        button_layout.addWidget(start_btn)
        button_layout.setSpacing(15)

        layout.addLayout(button_layout, 7, 0, 1, 2)

        self.setLayout(layout)

    def get_test_metadata(self) -> TestMetaData | None:
        return self.test_meta_data

    def handle_education_select(self, selected):
        """Aktualizuje i pokazuje drugi dropdown w zależności od wyboru."""
        if selected == School.PODSTAWOWE:
            options = [SchoolDetails.KLASA1, SchoolDetails.KLASA2, SchoolDetails.KLASA3, SchoolDetails.KLASA4,
                       SchoolDetails.KLASA5, SchoolDetails.KLASA6, SchoolDetails.KLASA7, SchoolDetails.KLASA8]
        elif selected == School.SREDNIE:
            options = [SchoolDetails.TECHNIKUM, SchoolDetails.LICEUM]
        elif selected == School.WYZSZE:
            options = [SchoolDetails.LICENCJAT, SchoolDetails.MAGISTER, SchoolDetails.DOKTORAT]
        else:
            options = []

        if options:
            self.details_dropdown.set_options(options)
            self.details_dropdown.show_widget()
        else:
            self.details_dropdown.hide_widget()

    def on_start_btn_click(self):
        fields = [self.first_name, self.last_name, self.date_of_birth, self.gender_radios,
                  self.eyes_radios, self.hands_radios, self.education_dropdown, self.details_dropdown, self.mode_radios]
        invalid_fields = [f for f in fields if not f.is_valid()]

        if invalid_fields:
            QMessageBox.warning(self, "Błąd", "Wypełnij wszystkie wymagane pola!")
            return

        # Dodawanie/update pacjenta do bazy danych
        print('name: ', self.first_name.get_value())
        print('name: ', self.last_name.get_value())
        print('date: ', self.date_of_birth.get_value())
        print("age:", calculate_age(self.date_of_birth.get_value()))
        print("gender:", self.gender_radios.get_value())
        print("hand:", self.hands_radios.get_value())
        print("eye:", self.eyes_radios.get_value())
        print("eye desc:", self.eyes_description.get_value())

        print("school", self.education_dropdown.get_value())
        print("details", self.details_dropdown.get_value())
        print("mode", self.mode_radios.get_value())
        print("additional_info", self.additional_info.get_value())
        print("examine_reason", self.examine_reason.get_value())

        years, months, days = calculate_age(self.date_of_birth.get_value())
        gender_value = self.gender_radios.get_value()  # np. "Mężczyzna"

        if gender_value == "Mężczyzna":
            gender_enum = Gender.MEZCZYZNA
        elif gender_value == "Kobieta":
            gender_enum = Gender.KOBIETA
        else:
            gender_enum = None

        hand_value = self.hands_radios.get_value()
        if hand_value == "Prawa":
            hand_enum = Hand.PRAWA
        elif hand_value == "Lewa":
            hand_enum = Hand.LEWA
        else:
            hand_enum = None
        patient = Patient(
            None,
            self.first_name.get_value(),
            self.last_name.get_value(),
            self.date_of_birth.get_value(),
            years,
            months,
            days,
            gender_enum,
            hand_enum,
            self.eyes_radios.get_value() == 'Tak',
            self.eyes_description.get_value()
        )
        patient_id = self.patientService.createOrUpdatePatient(patient)

        degree = PatientDegree(
            None,
            patient_id,
            self.education_dropdown.get_value(),
            self.details_dropdown.get_value()
        )
        degree_id = self.patientDegreeRepository.insert_patient_degree(degree)

        mode_value = self.mode_radios.get_value()
        if mode_value == "Normalny":
            mode_enum = Mode.NORMALNY
        elif mode_value == "Uproszczony":
            mode_enum = Mode.UPROSZCZONY
        else:
            mode_enum = None
        examination = Examination(
            None,
            patient_id,
            degree_id,
            mode_enum,
            date.today(),
            None,
            None,
            self.examine_reason.get_value()
        )
        examination_id = self.examinationRepository.insert_examination(examination)

        additional_info = Comment(
            patient_id=patient_id,
            comment=self.additional_info.get_value()
        )
        self.commentRepository.insert_comment(additional_info)

        afterwards_opinion = AfterwardsOpinion(
            examination_id,
            None
        )
        self.examineReasonRepository.insert_afterwards_opinion(afterwards_opinion)
        self.test_meta_data = TestMetaData(examination_id, patient_id)
        self.startRequested.emit()
