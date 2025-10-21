from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt

from components.StyledButton import StyledButton
from components.StyledCheckBox import StyledCheckBox
from components.StyledTextArea import StyledTextArea
from components.StyledTextInput import StyledTextInput


class MainForm(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        first_name = StyledTextInput("Imię", placeholder="Imię")
        last_name = StyledTextInput("Nazwisko", placeholder="Nazwisko")
        date_of_birth = StyledTextInput("Data urodzenia", placeholder="Data urodzenia", is_date=True)

        name_layout = QHBoxLayout()
        name_layout.setSpacing(10)
        name_layout.addWidget(first_name)
        name_layout.addWidget(last_name)

        name_layout.setStretch(0, 1)
        name_layout.setStretch(1, 1)

        layout.addLayout(name_layout, 0, 0)
        layout.addWidget(date_of_birth, 0, 1)

        gender_radios = StyledCheckBox("Płeć", ['Mężczyzna', 'Kobieta'], is_radio=True)
        hands_radios = StyledCheckBox("Ręka dominująca", ['Prawa', 'Lewa'], is_radio=True)

        layout.addWidget(gender_radios, 1, 0)
        layout.addWidget(hands_radios, 1, 1)

        eyes_radios = StyledCheckBox("Wada wzroku", ['Tak', 'Nie'], is_radio=True)
        eyes_description = StyledTextArea("Opis wady")
        eyes_description.setFixedHeight(eyes_radios.sizeHint().height())

        layout.addWidget(eyes_radios, 2, 0, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(eyes_description, 2, 1)

        additional_info = StyledTextArea("Uwagi")
        additional_info.setFixedHeight(150)

        layout.addWidget(additional_info, 3, 0, 1, 2)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # pushuje przyciski w prawo

        start_btn = StyledButton("Rozpocznij test", color="#89c057")
        start_btn.clicked.connect(on_start_btn_click)
        latest_examine_btn = StyledButton("Poprzednie badania", color="#EEB14C")
        latest_examine_btn.setDisabled(True)

        button_layout.addWidget(latest_examine_btn)
        button_layout.addWidget(start_btn)
        button_layout.setSpacing(15)  # odstęp między przyciskami

        # dodanie layoutu do siatki w wierszu 4 (ostatni), rozciągając na 2 kolumny
        layout.addLayout(button_layout, 4, 0, 1, 2)

        self.setLayout(layout)


def on_start_btn_click():
    print("DUPA")
