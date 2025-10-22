from PyQt6 import QtCore
from PyQt6.QtGui import QFont, QPixmap, QPainter
from PyQt6.QtWidgets import QLabel

FONT_SIZE = 30
HEIGHT = 100


def getFont() -> QFont:
    font = QFont()
    font.setPointSize(FONT_SIZE)
    font.setBold(True)
    return font


class StyledHeader(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(HEIGHT)
        self.setFont(getFont())
        self.setStyleSheet("""
                    background-color: #89c057;
                    color: black;
                    border-bottom: 3px solid #e0c77f;
                """)
