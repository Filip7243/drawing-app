from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QWidget, QLabel,
                             QVBoxLayout, QDateEdit, QLineEdit, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from datetime import date

class StyledTextInput(QWidget):
    def __init__(self, label_text, is_date=False, placeholder="", required=False):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(0)

        self.required = required
        self.is_date = is_date

        if self.required:
            label_text = f"{label_text} <sup style='color:red; font-size:14px;'>*</sup>"

        self.label = QLabel(label_text)
        self.label.setTextFormat(Qt.TextFormat.RichText)
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

    def is_valid(self):
        value = self.input.text().strip()
        return bool(value) if self.required else True

    def get_value(self):
        if self.is_date:
            form_date = self.input.date()
            return date(form_date.year(), form_date.month(), form_date.day())

        return self.input.text().strip()
