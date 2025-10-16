from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PySide6.QtWidgets import (
    QLabel
)

FONT_SIZE = 28

HEIGHT = 100


def getFont() -> QFont:
    font = QFont()
    font.setPointSize(FONT_SIZE)
    font.setBold(True)
    return font


class StyledHeader(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(HEIGHT)
        self.setFont(getFont())
        self.setStyleSheet("background-color: #89c057; color: white; border-radius: 10px;")
