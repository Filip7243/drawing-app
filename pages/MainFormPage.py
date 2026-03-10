from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout, QMessageBox

from components.MainForm import MainForm
from components.StyledHeader import StyledHeader
from components.LatestPatients import LatestPatients
from db.models import PatientIdentity, Gender, Hand
from db.repository.PatientRepository import PatientRepository
from pages.EarlierExaminesPage import EarlierExaminesPage
from pages.LatestExaminationsPage import LatestExaminationsPage

CONTENT_MARGINS = 100
SPACING = 100


class MainFormPage(QWidget):
    startRequested = pyqtSignal()
    patientRepo = PatientRepository()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.background = QPixmap("assets:img/background.png")
        self.scaled_background = self.background
        self.setWindowTitle("Main Form Page")

        self.stacked_layout = QStackedLayout()

        # Widget 1: MainForm + header
        self.main_widget = QWidget()
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)

        header = StyledHeader("BVRT TEST")
        main_layout.addWidget(header)

        form_container = QHBoxLayout()
        form_container.addStretch(1)

        self.main_form = MainForm(parent=self)
        self.main_form.startRequested.connect(self.startRequested.emit)

        form_container.addWidget(self.main_form, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.latest_patients = LatestPatients(parent=self)
        self.latest_patients.setFixedWidth(300)
        self.latest_patients.patientSelected.connect(self.main_form.fill_patient_data)
        form_container.addWidget(self.latest_patients)

        form_container.addStretch(1)
        main_layout.addLayout(form_container)

        # Widget 2: EarlierExaminesPage (bez wczytywania danych na starcie)
        self.earlier_page = EarlierExaminesPage(parent=self)
        self.main_form.showEarlierRequested.connect(self.show_earlier_page)
        self.earlier_page.backRequested.connect(self.show_main_form)

        # Widget 3: LatestExaminationsPage
        self.latest_exams_page = LatestExaminationsPage(parent=self)
        self.main_form.showLatestExamsRequested.connect(self.show_latest_exams_page)
        self.latest_exams_page.backRequested.connect(self.show_main_form)

        # Dodajemy widgety do stacked layout
        self.stacked_layout.addWidget(self.main_widget)
        self.stacked_layout.addWidget(self.earlier_page)
        self.stacked_layout.addWidget(self.latest_exams_page)

        self.stacked_layout.setCurrentWidget(self.main_widget)

        # Ustawiamy główny layout tego widgetu na stacked_layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.stacked_layout)

    def show_earlier_page(self):
        valid, msg = self.main_form.validate_fields()
        if not valid:
            QMessageBox.warning(self, "Błąd walidacji", msg)
            return

        gender_value = self.main_form.gender_radios.get_value()

        if gender_value == "Mężczyzna":
            gender_enum = Gender.MEZCZYZNA
        elif gender_value == "Kobieta":
            gender_enum = Gender.KOBIETA
        else:
            gender_enum = None

        hand_value = self.main_form.hands_radios.get_value()
        if hand_value == "Prawa":
            hand_enum = Hand.PRAWA
        elif hand_value == "Lewa":
            hand_enum = Hand.LEWA
        else:
            hand_enum = None
        patient = self.patientRepo.get_patient_by_identity(
            self.main_form.first_name.get_value(),
            self.main_form.last_name.get_value(),
            self.main_form.date_of_birth.get_value(),
            gender_enum,
            hand_enum
        )
        patient_identity = PatientIdentity(
            patient.id,
            self.main_form.first_name.get_value(),
            self.main_form.last_name.get_value(),
            self.main_form.date_of_birth.get_value(),
            gender_enum,
            hand_enum
        )

        self.earlier_page.load_patient(patient_identity)

        self.stacked_layout.setCurrentWidget(self.earlier_page)

    def show_main_form(self):
        self.stacked_layout.setCurrentWidget(self.main_widget)

    def show_latest_exams_page(self):
        self.latest_exams_page.load_data()
        self.stacked_layout.setCurrentWidget(self.latest_exams_page)

    def resizeEvent(self, event):
        if not self.background.isNull():
            self.scaled_background = self.background.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.scaled_background.isNull():
            x = (self.width() - self.scaled_background.width()) // 2
            y = (self.height() - self.scaled_background.height()) // 2
            painter.drawPixmap(x, y, self.scaled_background)
        super().paintEvent(event)
