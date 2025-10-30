from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QGraphicsDropShadowEffect


class StyledLegend(QWidget):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.items = items or []
        self._setup_ui()

    def _setup_ui(self):
        # Główny layout komponentu
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Ramka — jedyna z borderem i cieniem
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #bfbfbf;
                border-radius: 6px;
                background-color: #ffffff;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 60))
        frame.setGraphicsEffect(shadow)

        inner_layout = QHBoxLayout(frame)
        inner_layout.setContentsMargins(15, 10, 15, 10)
        inner_layout.setSpacing(25)  # odstęp między tekstami

        for text in self.items:
            label = QLabel(text)
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 12pt;
                    border: none;
                }
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            inner_layout.addWidget(label)

        inner_layout.addStretch()

        main_layout.addWidget(frame)
