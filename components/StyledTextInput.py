from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QDateEdit, QLineEdit


class StyledTextInput(QWidget):
    def __init__(self, label_text, is_date=False, placeholder=""):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        self.label = QLabel(label_text)
        self.label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(self.label)

        if is_date:
            self.input = QDateEdit()
            self.input.setCalendarPopup(True)
            self.input.setDisplayFormat("dd.MM.yyyy")
        else:
            self.input = QLineEdit()
            self.input.setPlaceholderText(placeholder)

        self.input.setStyleSheet("""
            QLineEdit, QDateEdit {
                font-size: 14pt;
                padding: 6px;
                border: 2px solid #f8e8c5;
                border-radius: 6px;
                background-color: white;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #89c057;
            }
        """)
        layout.addWidget(self.input)
        self.setLayout(layout)
