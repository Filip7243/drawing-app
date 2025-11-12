from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from components.EarlierExaminesTable import EarlierExaminesTable
from components.StyledHeader import StyledHeader
from components.StyledLegend import StyledLegend
from db.models import PatientIdentity
from db.service.ExaminationService import ExaminationService


class EarlierExaminesPage(QWidget):
    backRequested = pyqtSignal()
    examinationService = ExaminationService()

    def __init__(self, parent=None, legend_items=None, patient_identity: PatientIdentity | None = None):
        super().__init__(parent)

        self.background = QPixmap("assets:img/background.png")
        self.scaled_background = self.background
        self.setWindowTitle("Results Page")

        # -----------------------------
        # Główny layout strony
        # -----------------------------
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # -----------------------------
        # Header
        # -----------------------------
        self.header = StyledHeader("Pacjent P0001", show_back_button=True)
        main_layout.addWidget(self.header)

        self.header.back_button.clicked.connect(self.backRequested.emit)

        # Spacer górny - wypycha content w dół
        main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # -----------------------------
        # HBox: tabela po lewej, PatientSummary po prawej
        # -----------------------------
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Tabela wyników
        self.table_widget = EarlierExaminesTable(table_data=list())
        self.table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(self.table_widget)

        # Jeśli przekazano patient_identity przy tworzeniu strony, wczytaj dane
        if patient_identity:
            self.load_patient(patient_identity)

        main_layout.addLayout(content_layout)

        # Spacer dolny - wypycha content w górę
        main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # -----------------------------
        # Legenda
        # -----------------------------
        legend_items = legend_items or [
            "Śr. - Średni czas spędzony na rysowaniu jednego wzoru",
            "Cał. - Całościowy czas testu (rysowania)"
        ]
        legend = StyledLegend(items=legend_items)
        legend.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(legend, alignment=Qt.AlignmentFlag.AlignCenter)

    def load_patient(self, patient_identity: PatientIdentity):
        try:
            header_text = f"Pacjent {patient_identity.id}"
        except Exception:
            header_text = "Pacjent XXXX"
        self.header.set_title(header_text)

        latest_examinations = self.examinationService.get_patient_previous_examinations(patient_identity)
        self.table_widget.set_data(latest_examinations)
        self.table_widget.table.resizeRowsToContents()
        self.table_widget.table.setFixedHeight(self.table_widget.table.verticalHeader().length())

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
