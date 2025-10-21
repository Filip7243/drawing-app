from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from components.AprilTagsComponent import AprilTagsComponent
from components.StyledButton import StyledButton
from components.StyledHeader import StyledHeader


class DrawingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Draw Figure Page")
        self.showMaximized()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)  # brak marginesów

        header = StyledHeader("Odwzoruj rysunek")
        main_layout.addWidget(header)

        # TODO: zapytać się czy canvas ma być na całej stronie,
        # TODO: czy ma być docięty do april tagów,
        # TODO: bo z tym może być później problem jeśli chodzi
        # TODO: o mapowanie współrzędnych itp. z okularów na obraz 2D
        april_tags = AprilTagsComponent(num_tags=4, show_canvas=True)
        main_layout.addWidget(april_tags)

        button_container = QWidget()
        button_container.setStyleSheet("background-color: #FFEDCC;")
        # Layout w kontenerze
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)

        # Przycisk
        done_button = StyledButton("Zakończ")
        button_layout.addStretch()
        button_layout.addWidget(done_button)
        button_layout.addStretch()

        button_container.setFixedHeight(done_button.sizeHint().height())

        main_layout.addWidget(button_container)

        self.setLayout(main_layout)
