from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from components.MainForm import MainForm
from components.StyledHeader import StyledHeader

CONTENT_MARGINS = 100
SPACING = 100


class MainFormPage(QWidget):
    startRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.background = QPixmap("assets:img/background.png")
        self.scaled_background = self.background
        self.setWindowTitle("Main Form Page")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)

        header = StyledHeader("BVRT TEST")
        main_layout.addWidget(header)

        form_container = QHBoxLayout()
        form_container.addStretch(1)

        main_form = MainForm(parent=self)
        main_form.startRequested.connect(self.startRequested.emit)
        form_container.addWidget(main_form, alignment=Qt.AlignmentFlag.AlignCenter)
        form_container.addStretch(1)
        main_layout.addLayout(form_container)

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        if not self.background.isNull():
            self.scaled_background = self.background.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.scaled_background.isNull():
            x = (self.width() - self.scaled_background.width()) // 2
            y = (self.height() - self.scaled_background.height()) // 2
            painter.drawPixmap(x, y, self.scaled_background)
        super().paintEvent(event)
