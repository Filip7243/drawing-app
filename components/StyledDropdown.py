from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QComboBox, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor, QMouseEvent, QIcon
from PyQt6.QtCore import Qt, QTimer, QObject


class StyledDropdown(QWidget):
    def __init__(self, label_text, options=None, placeholder="Wybierz...", on_select=None, is_hidden=False):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(0)

        self.label = QLabel(label_text)
        self.label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(self.label)

        self.combo = QComboBox()
        self.combo.setEditable(False)
        self.combo.setCursor(Qt.CursorShape.PointingHandCursor)

        self.combo.addItem(placeholder)
        self.combo.model().item(0).setEnabled(False)

        if options:
            self.combo.addItems(options)

        self.combo.setStyleSheet("""
            QComboBox {
                font-size: 14pt;
                padding: 6px 35px 6px 6px; /* dodaj padding po prawej na strzałkę */
                border: 2px solid #e0c77f;
                border-radius: 6px;
                background-color: white;
                font-weight: bold;
            }
            QComboBox:hover {
                border: 3px solid #d8b44a;
            }
            QComboBox:focus {
                border: 3px solid #e0c77f;
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
        if index == 0:
            self.combo.setCurrentIndex(0)
            return
        if self.on_select:
            value = self.combo.currentText()
            self.on_select(value)

    def set_options(self, options):
        # zachowaj placeholder jako pierwszy element
        self.combo.clear()
        self.combo.addItem("Wybierz...")
        self.combo.model().item(0).setEnabled(False)
        if options:
            self.combo.addItems(options)

    def get_value(self):
        # zwraca None, jeśli wybrano placeholder
        if self.combo.currentIndex() == 0:
            return None
        return self.combo.currentText()

    def show_widget(self):
        self.setVisible(True)

    def hide_widget(self):
        self.setVisible(False)
