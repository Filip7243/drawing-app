from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy

from components.MainForm import MainForm
from components.StyledHeader import StyledHeader

CONTENT_MARGINS = 100
SPACING = 100


class MainFormPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background = QPixmap("assets:img/background.png")
        self.scaled_background = self.background
        self.setWindowTitle("Main Form Page")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(50)
        main_layout.setContentsMargins(0, 0, 0, 0)  # brak marginesów

        header = StyledHeader("BVRT TEST")
        main_layout.addWidget(header)  # header zajmuje pełną szerokość

        form_container = QHBoxLayout()
        form_container.addStretch(1)

        main_form = MainForm()
        form_container.addWidget(main_form, alignment=Qt.AlignmentFlag.AlignCenter)
        form_container.addStretch(1)

        # dodaj form do głównego layoutu
        main_layout.addLayout(form_container)
        main_layout.addStretch(1)  # lekki bufor na dole

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        """Skaluje tło tylko przy zmianie rozmiaru."""
        if not self.background.isNull():
            self.scaled_background = self.background.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        super().resizeEvent(event)

    def paintEvent(self, event):
        """Rysuje przeskalowane tło wyśrodkowane."""
        painter = QPainter(self)
        if not self.scaled_background.isNull():
            x = (self.width() - self.scaled_background.width()) // 2
            y = (self.height() - self.scaled_background.height()) // 2
            painter.drawPixmap(x, y, self.scaled_background)
        super().paintEvent(event)
