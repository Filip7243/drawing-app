from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from db.repository.PatientRepository import PatientRepository
from db.models import Patient

class LatestPatients(QWidget):
    patientSelected = pyqtSignal(Patient)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_repo = PatientRepository()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.label = QLabel("Ostatni pacjenci")
        self.label.setStyleSheet("font-size: 12pt; font-weight: bold; color: black;")
        layout.addWidget(self.label)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 2px solid #e0c77f;
                border-radius: 6px;
                background-color: white;
                color: black;
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
                color: black;
            }
            QListWidget::item:selected {
                background-color: #f9e8cc;
                color: black;
            }
        """)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.list_widget)
        
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        patients = self.patient_repo.get_latest_patients(limit=30)
        for p in patients:
            item = QListWidgetItem(f"{p.first_name} {p.last_name}")
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        patient = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(patient, Patient):
            self.patientSelected.emit(patient)
