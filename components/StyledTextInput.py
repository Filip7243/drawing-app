from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QWidget, QLabel,
                             QVBoxLayout, QDateEdit, QLineEdit, QGraphicsDropShadowEffect)


class StyledTextInput(QWidget):
    def __init__(self, label_text, is_date=False, placeholder=""):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.label = QLabel(label_text)
        self.label.setStyleSheet("font-size: 10pt; font-weight: bold;")
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
                font-size: 12pt;
                padding: 6px;
                border: 2px solid #e0c77f;
                border-radius: 6px;
                background-color: white;
                font-weight: bold;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 3px solid #e0c77f;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)  # rozmycie cienia
        shadow.setOffset(0, 5)  # przesunięcie: x=0, y=2
        shadow.setColor(QColor(0, 0, 0, 80))  # kolor i przezroczystość
        self.input.setGraphicsEffect(shadow)

        layout.addWidget(self.input)
        self.setLayout(layout)
