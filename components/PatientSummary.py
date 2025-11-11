from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QPushButton, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
)

from components.StyledButton import StyledButton
from db.models import PatientSummaryDTO
from db.repository.PatientRepository import PatientRepository


def _create_info_row(label_text: str, value_text: str) -> QHBoxLayout:
    """Tworzy poziomy wiersz etykieta: wartość (justify-content: space-between)"""
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    label = QLabel(label_text)
    label.setStyleSheet("font-weight: bold; font-size: 13pt;")
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    value = QLabel(value_text)
    value.setStyleSheet("font-size: 13pt;")
    value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    layout.addWidget(label, 1, Qt.AlignmentFlag.AlignLeft)
    layout.addWidget(value, 1, Qt.AlignmentFlag.AlignRight)

    return layout


class PatientSummary(QWidget):
    patientRepository = PatientRepository()

    def __init__(self, patient_id=None, parent=None):
        super().__init__(parent)

        patient: PatientSummaryDTO = self.patientRepository.get_patient_summary_by_id(patient_id=patient_id)

        # Dane przykładowe jeśli brak
        self.patient_data = {
            "pacjent": patient.id,
            "plec": patient.gender,
            "wiek": f"{patient.age_years} lat, {patient.age_months} miesięcy, {patient.age_days} dni",
            "reka": patient.dominant_hand,
            "wada": patient.eye_description,
            "uwagi": patient.comment,
            "funkcje": "W normie",
        }

        print("self.patient_data: ", self.patient_data)

        self._setup_ui()

    def _setup_ui(self):
        print("WHAAT?!")
        try:
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(15)

            frame = QFrame()
            frame.setStyleSheet("""
                    QFrame {
                        border: 1px solid #c0c0c0;
                        border-radius: 4px;
                        background-color: #ffffff;
                    }
                """)
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(20, 20, 20, 20)
            frame_layout.setSpacing(12)

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setOffset(0, 5)
            shadow.setColor(QColor(0, 0, 0, 60))
            frame.setGraphicsEffect(shadow)

            info_items = [
                ("Pacjent:", self.patient_data.get("pacjent")),
                ("Płeć:", self.patient_data.get("plec")),
                ("Wiek:", self.patient_data.get("wiek")),
                ("Ręka:", self.patient_data.get("reka")),
                ("Wada wzroku:", self.patient_data.get("wada")),
                ("Wynik testu sugeruje:", "funkcje wzrokowo-przestrzenne w normie")
            ]

            for label, value in info_items:
                frame_layout.addLayout(_create_info_row(label, str(value)))

            comments_layout = QHBoxLayout()
            comments_label = QLabel("Uwagi:")
            comments_label.setStyleSheet("font-weight: bold; font-size: 13pt;")

            show_button = QPushButton("Pokaż")
            show_button.setCursor(Qt.CursorShape.PointingHandCursor)
            show_button.setStyleSheet("""
                    QPushButton {
                        background-color: #eeeeee;
                        border-radius: 4px;
                        padding: 4px 10px;
                    }
                    QPushButton:hover {
                        background-color: #dddddd;
                    }
                """)
            show_button.clicked.connect(self.on_show_clicked)

            comments_layout.addWidget(comments_label, 1, Qt.AlignmentFlag.AlignLeft)
            comments_layout.addWidget(show_button, 1, Qt.AlignmentFlag.AlignRight)
            comments_layout.addStretch()
            frame_layout.addLayout(comments_layout)

            frame_layout.addItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

            end_btn = StyledButton("KONIEC", color="#d9534f", font_color="white")
            end_btn.setFixedWidth(200)
            end_btn.setCursor(Qt.CursorShape.PointingHandCursor)

            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(end_btn)
            btn_layout.addStretch()

            frame_layout.addLayout(btn_layout)
            main_layout.addWidget(frame)
            print("ESSSSA!")

        except Exception as e:
            import traceback
            print("💥 Błąd w setup_ui:", e)
            print(traceback.format_exc())

    def on_show_clicked(self):
        print("Kliknięto 'Pokaż' w sekcji Uwagi (popup w przyszłości)")
