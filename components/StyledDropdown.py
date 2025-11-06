from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox, QGraphicsDropShadowEffect
from enum import Enum


class StyledDropdown(QWidget):
    def __init__(self, label_text, options=None, placeholder="Wybierz...", on_select=None, is_hidden=False, required=False):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(0)

        self.required = required

        if self.required:
            label_text = f"{label_text} <sup style='color:red; font-size:14px;'>*</sup>"

        self.label = QLabel(label_text)
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        layout.addWidget(self.label)

        self.combo = QComboBox()
        self.combo.setEditable(False)
        self.combo.setCursor(Qt.CursorShape.PointingHandCursor)

        self.combo.addItem(placeholder, userData=None)
        self.combo.model().item(0).setEnabled(False)

        if options:
            self.set_options(options)

        self.combo.setStyleSheet("""
            QComboBox {
                font-size: 12pt;
                padding: 6px;
                border: 2px solid #e0c77f;
                border-radius: 6px;
                background-color: white;
                font-weight: bold;
            }
            QComboBox:hover {
                border: 2px solid #d8b44a;
            }
            QComboBox:focus {
                border: 2px solid #e0c77f;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.combo.setGraphicsEffect(shadow)

        layout.addWidget(self.combo)
        self.setLayout(layout)

        self.on_select = on_select
        if on_select:
            self.combo.currentIndexChanged.connect(self._handle_select)

        self.setVisible(not is_hidden)

    def _handle_select(self, index):
        if index <= 0:
            return
        if self.on_select:
            selected_enum = self.combo.currentData()
            self.on_select(selected_enum)

    def set_options(self, options):
        """Przyjmuje listę Enumów lub stringów."""
        self.combo.clear()
        self.combo.addItem("Wybierz...", userData=None)
        self.combo.model().item(0).setEnabled(False)

        if not options:
            return

        for opt in options:
            if isinstance(opt, Enum):
                # Pokazujemy nazwę w formie czytelnej (np. z dużą literą)
                label = opt.name.capitalize().replace("_", " ")
                self.combo.addItem(label, userData=opt)
            else:
                self.combo.addItem(str(opt), userData=opt)

    def get_value(self):
        """Zwraca Enum, jeśli wybrano Enum — inaczej None."""
        if self.combo.currentIndex() == 0:
            return None
        return self.combo.currentData()

    def show_widget(self):
        self.setVisible(True)

    def hide_widget(self):
        self.setVisible(False)

    def is_valid(self):
        return self.combo.currentIndex() > 0 if self.required else True
