from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QGraphicsDropShadowEffect


class StyledTextArea(QWidget):
    def __init__(self, placeholder=""):
        super().__init__()
        layout = QVBoxLayout()

        self.textarea = QTextEdit()
        self.textarea.setPlaceholderText(placeholder)
        self.textarea.setStyleSheet("""
            QTextEdit {
                font-size: 12pt;
                padding: 6px;
                border: 2px solid #e0c77f;
                border-radius: 6px;
                background-color: white;
                font-weight: bold;
            }
            QTextEdit:focus {
                border: 3px solid #e0c77f;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)  # rozmycie cienia
        shadow.setOffset(0, 5)  # przesunięcie: x=0, y=2
        shadow.setColor(QColor(0, 0, 0, 80))  # kolor i przezroczystość
        self.textarea.setGraphicsEffect(shadow)

        layout.addWidget(self.textarea)
        self.setLayout(layout)

    def get_value(self):
        return self.textarea.toPlainText()
