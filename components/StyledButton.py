from PyQt6.QtWidgets import QPushButton


class StyledButton(QPushButton):
    def __init__(self, text, color="#89c057"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 14pt;
                border-radius: 8px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: #78a548;
            }}
            QPushButton:pressed {{
                background-color: #5f8435;
            }}
        """)
