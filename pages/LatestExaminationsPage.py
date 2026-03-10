from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from components.StyledHeader import StyledHeader
from components.LatestExaminationsTable import LatestExaminationsTable
from db.repository.ExaminationRepository import ExaminationRepository

class LatestExaminationsPage(QWidget):
    backRequested = pyqtSignal()
    examRepo = ExaminationRepository()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(50, 20, 50, 50)
        self.layout.setSpacing(20)

        # Nagłówek
        self.header = StyledHeader("OSTATNIE BADANIA")
        self.layout.addWidget(self.header)

        # Tabela
        self.exams_table = LatestExaminationsTable([], parent=self)
        self.layout.addWidget(self.exams_table)

        # Przycisk powrotu
        self.bottom_layout = QHBoxLayout()
        self.back_button = QPushButton("Powrót")
        self.back_button.setFixedWidth(150)
        self.back_button.setFixedHeight(40)
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5a6268; }
        """)
        self.back_button.clicked.connect(self.backRequested.emit)
        
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.back_button)
        self.bottom_layout.addStretch()
        
        self.layout.addLayout(self.bottom_layout)

    def load_data(self):
        exams = self.examRepo.get_latest_examinations(limit=30)
        self.exams_table.set_data(exams)
