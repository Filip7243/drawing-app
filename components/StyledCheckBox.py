from PyQt6.QtWidgets import QHBoxLayout, QRadioButton, QCheckBox, QGroupBox


class StyledCheckBox(QGroupBox):
    def __init__(self, title, options, is_radio=True):
        super().__init__(title)
        self.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                margin-top: 10px;
            }
        """)
        layout = QHBoxLayout()
        self.buttons = []
        for opt in options:
            btn = QRadioButton(opt) if is_radio else QCheckBox(opt)
            btn.setStyleSheet(f"""
                QRadioButton, QCheckBox {{
                    font-size: 12pt;
                    spacing: 10px;
                    border: 2px solid #f8e8c5;
                    border-radius: 6px;
                    padding: 4px;
                    background-color: white;
                }}
                QRadioButton:checked {{
                    background-color: #f9e8cc;
                }}
                QCheckBox:checked {{
                    background-color: #f9e8cc;
                }}
            """)
            layout.addWidget(btn)
            self.buttons.append(btn)  ## TODO: to do wyrzucenia chyba
        self.setLayout(layout)
