from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout

from components.StyledButton import StyledButton
from components.StyledCheckBox import StyledCheckBox
from components.StyledDropdown import StyledDropdown
from components.StyledTextArea import StyledTextArea
from components.StyledTextInput import StyledTextInput


class MainForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = QGridLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 8, 8, 8)

        first_name = StyledTextInput("Imię", placeholder="Imię")
        last_name = StyledTextInput("Nazwisko", placeholder="Nazwisko")
        date_of_birth = StyledTextInput("Data urodzenia", placeholder="Data urodzenia", is_date=True)

        name_layout = QHBoxLayout()
        name_layout.setSpacing(2)
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

        dropdown_row = QHBoxLayout()
        dropdown_row.setSpacing(50)

        # pierwszy dropdown — zawsze widoczny
        self.education_dropdown = StyledDropdown(
            label_text="Wykształcenie",
            options=["Podstawowe", "Średnie", "Wyższe"],
            placeholder="Wybierz poziom wykształcenia...",
            on_select=self.handle_education_select
        )
        dropdown_row.addWidget(self.education_dropdown)

        # drugi dropdown — ukryty na start
        self.details_dropdown = StyledDropdown(
            label_text="Szczegóły",
            placeholder="Wybierz szczegóły...",
            is_hidden=True
        )
        dropdown_row.addWidget(self.details_dropdown)

        layout.addLayout(dropdown_row, 3, 0, 1, 2)

        additional_info = StyledTextArea("Uwagi")
        additional_info.setFixedHeight(120)

        layout.addWidget(additional_info, 4, 0, 1, 2)

        examine_reason = StyledTextArea("Powód badania")
        examine_reason.setFixedHeight(100)

        layout.addWidget(examine_reason, 5, 0, 1, 2)

        mode_radios = StyledCheckBox("Tryb testu", ['Normalny', 'Uproszczony'], is_radio=True)

        layout.addWidget(mode_radios, 6, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter)

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

    def handle_education_select(self, selected):
        """Aktualizuje i pokazuje drugi dropdown w zależności od wyboru."""
        if selected == "Podstawowe":
            options = [f"Klasa {i}" for i in range(1, 9)]
        elif selected == "Średnie":
            options = ["Technikum", "Liceum"]
        elif selected == "Wyższe":
            options = ["Licencjat", "Magister", "Doktorat"]
        else:
            options = []

        if options:
            self.details_dropdown.set_options(options)
            self.details_dropdown.show_widget()
        else:
            self.details_dropdown.hide_widget()

    def on_start_btn_click(self):
        pass
