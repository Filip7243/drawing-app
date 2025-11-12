from PyQt6 import QtCore
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QWidget

from components.IconButton import IconButton

FONT_SIZE = 30
HEIGHT = 100


def getFont() -> QFont:
    font = QFont()
    font.setPointSize(FONT_SIZE)
    font.setBold(True)
    return font


class StyledHeader(QWidget):
    def __init__(self, text, show_back_button=False, on_back_clicked=None, parent=None):
        """
        :param text: Tekst nagłówka
        :param show_back_button: Czy wyświetlać przycisk powrotu
        :param on_back_clicked: Funkcja wywoływana po kliknięciu 'Powrót'
        """
        super().__init__(parent)
        self.setFixedHeight(HEIGHT)
        self.setStyleSheet("""
                    background-color: #89c057;
                    border-bottom: 3px solid #e0c77f;
                """)

        # Główny napis - wycentrowany
        self.label = QLabel(text, self)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(getFont())
        self.label.setStyleSheet("color: black;")
        self.label.setGeometry(0, 0, self.width(), HEIGHT)

        # Opcjonalny przycisk powrotu z ikoną
        if show_back_button:
            self.back_button = IconButton("assets:icons/arrow-left.png", color="#f6f6f6", icon_size=24)
            self.back_button.move(20, (HEIGHT - self.back_button.height()) // 2)
            self.back_button.setParent(self)

            if callable(on_back_clicked):
                self.back_button.clicked.connect(on_back_clicked)

    def set_title(self, text):
        self.label.setText(text)

    def resizeEvent(self, event):
        """Aktualizuj pozycję labela przy zmianie rozmiaru"""
        super().resizeEvent(event)
        self.label.setGeometry(0, 0, self.width(), HEIGHT)
