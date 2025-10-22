from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor


def darken_color(hex_color, factor=0.85):
    """Przyciemnia kolor HEX o dany współczynnik (0-1)"""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))

    return f"#{r:02x}{g:02x}{b:02x}"


class StyledButton(QPushButton):
    def __init__(self, text, color="#89c057", font_color=None):
        super().__init__(text)

        hover_color = darken_color(color, 0.95)  # ciemniejszy o 15%
        pressed_color = darken_color(color, 0.9)  # ciemniejszy o 30%

        self.font_color = font_color or "black"

        print(self.font_color)

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {self.font_color};
                font-size: 16pt;
                border-radius: 4px;
                padding: 10px 20px;
                border: 2px solid #e0c77f;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:disabled {{
                background-color: #e0e0e0;  /* jaśniejszy szary */
                color: #aaaaaa;             /* ciemniejszy szary tekst */
                border: 2px solid #cccccc;  /* lekko szara ramka */
            }}
        """)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)  # rozmycie cienia
        shadow.setOffset(0, 5)  # przesunięcie: x=0, y=2
        shadow.setColor(QColor(0, 0, 0, 80))  # kolor i przezroczystość
        self.setGraphicsEffect(shadow)
