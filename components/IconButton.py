from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor, QIcon


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


class IconButton(QPushButton):
    def __init__(self, icon_path, color="#89c057", icon_size=24):
        """
        :param icon_path: Ścieżka do pliku ikony (np. "icons/back.png")
        :param color: Kolor tła przycisku
        :param icon_size: Rozmiar ikony w pikselach
        """
        super().__init__()

        hover_color = darken_color(color, 0.95)  # ciemniejszy o 5%
        pressed_color = darken_color(color, 0.9)  # ciemniejszy o 10%

        # Ustawienie ikony
        icon = QIcon(icon_path)
        self.setIcon(icon)
        self.setIconSize(QSize(icon_size, icon_size))

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 4px;
                padding: 6px;
                border: 2px solid #e0c77f;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:disabled {{
                background-color: #e0e0e0;
                border: 2px solid #cccccc;
            }}
        """)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Cień
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        # Domyślny rozmiar przycisku (kwadratowy)
        button_size = icon_size + 16  # padding 8px z każdej strony
        self.setFixedSize(button_size, button_size)
