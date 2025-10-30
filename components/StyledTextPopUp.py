from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QFrame, QGraphicsDropShadowEffect)


class StyledTextPopUp(QWidget):
    def __init__(self, header_text, content_text, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setMinimumSize(350, 400)

        # Główny kontener
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e0c77f;
                border-radius: 2px;
            }
        """)

        # Layout kontenera
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)
        container_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        self.header = QLabel(header_text)
        self.header.setTextFormat(Qt.TextFormat.RichText)
        self.header.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #333;
            border: none;
        """)
        self.header.setWordWrap(True)
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.header, 1)

        # Linia oddzielająca
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            QFrame {
                background-color: #e0c77f;
                border: none;
                max-height: 2px;
                min-height: 2px;
            }
        """)
        container_layout.addWidget(separator, 0)

        # Zawartość
        self.content = QLabel(content_text)
        self.content.setTextFormat(Qt.TextFormat.RichText)
        self.content.setStyleSheet("""
            font-size: 10pt;
            color: #555;
            border: none;
            line-height: 1;
        """)
        self.content.setWordWrap(True)
        self.content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.content, 2)

        # Layout główny
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        self.setLayout(main_layout)
