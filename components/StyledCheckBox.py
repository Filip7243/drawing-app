from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QHBoxLayout, QRadioButton, QCheckBox, QWidget, QLabel, QVBoxLayout, \
    QGraphicsDropShadowEffect


class StyledCheckBox(QWidget):
    def __init__(self, title, options, is_radio=True, required=False):
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(2)

        self.required = required
        self.is_radio = is_radio

        if self.required:
            title = f"{title} <sup style='color:red; font-size:14px;'>*</sup>"

        self.label = QLabel(title)
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.setStyleSheet("font-size: 10pt; font-weight: bold;")

        main_layout.addWidget(self.label)

        # layout dla samych przycisków
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)

        self.buttons = []
        for opt in options:
            btn = QRadioButton(opt) if is_radio else QCheckBox(opt)
            btn.setStyleSheet(f"""
                QRadioButton, QCheckBox {{
                    font-size: 12pt;
                    spacing: 10px;
                    border-radius: 6px;
                    padding: 6px;
                    background-color: white;
                    border: 2px solid #e0c77f;
                    font-weight: bold;
                }}
               
                QRadioButton:checked, QCheckBox:checked {{
                    background-color: #f9e8cc;
                    border: 3px solid #e0c77f;
                }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            buttons_layout.addWidget(btn)

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(5)  # rozmycie cienia
            shadow.setOffset(0, 5)  # przesunięcie: x=0, y=2
            shadow.setColor(QColor(0, 0, 0, 80))  # kolor i przezroczystość
            btn.setGraphicsEffect(shadow)

            self.buttons.append(btn)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def get_value(self):
        selected = [btn.text() for btn in self.buttons if btn.isChecked()]
        if not selected:
            return None
        # jeśli radio — tylko jedna wartość
        return selected[0] if self.is_radio else selected

    def is_valid(self):
        if not self.required:
            return True

        any_checked = any(btn.isChecked() for btn in self.buttons)
        return any_checked
