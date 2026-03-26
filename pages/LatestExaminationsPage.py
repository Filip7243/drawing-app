from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from components.StyledHeader import StyledHeader
from components.LatestExaminationsTable import LatestExaminationsTable
from db.repository.ExaminationRepository import ExaminationRepository
from pdf.ExcelGenerator import ExcelGenerator

class LatestExaminationsPage(QWidget):
    backRequested = pyqtSignal()
    examRepo = ExaminationRepository()
    excel_generator = ExcelGenerator()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(50, 20, 50, 50)
        self.layout.setSpacing(20)

        # Nagłówek i przycisk Excel w jednej linii
        header_layout = QHBoxLayout()
        self.header = StyledHeader("OSTATNIE BADANIA")
        header_layout.addWidget(self.header)
        
        header_layout.addStretch()
        
        self.excel_button = QPushButton("Eksportuj wszystko do Excel")
        self.excel_button.setFixedWidth(250)
        self.excel_button.setFixedHeight(40)
        self.excel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.excel_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        self.excel_button.clicked.connect(self.export_to_excel)
        header_layout.addWidget(self.excel_button)
        
        self.layout.addLayout(header_layout)

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

    def export_to_excel(self):
        try:
            output_path = self.excel_generator.generate_global_report()
            QMessageBox.information(self, "Sukces", f"Raport Excel został wygenerowany pomyślnie:\n{output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas generowania raportu:\n{str(e)}")
