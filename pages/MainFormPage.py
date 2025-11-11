from pages.EarlierExaminesPage import EarlierExaminesPage

CONTENT_MARGINS = 100
SPACING = 100

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout, QMessageBox

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

        self.stacked_layout = QStackedLayout()

        # Widget 1: MainForm + header
        self.main_widget = QWidget()
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)

        header = StyledHeader("BVRT TEST")
        main_layout.addWidget(header)

        form_container = QHBoxLayout()
        form_container.addStretch(1)

        self.main_form = MainForm(parent=self)
        self.main_form.startRequested.connect(self.startRequested.emit)

        form_container.addWidget(self.main_form, alignment=Qt.AlignmentFlag.AlignCenter)
        form_container.addStretch(1)
        main_layout.addLayout(form_container)

        # Widget 2: EarlierExaminesPage
        self.earlier_page = EarlierExaminesPage(parent=self)

        self.main_form.showEarlierRequested.connect(self.show_earlier_page)
        self.earlier_page.backRequested.connect(self.show_main_form)

        # Dodajemy oba widgety do stacked layout
        self.stacked_layout.addWidget(self.main_widget)
        self.stacked_layout.addWidget(self.earlier_page)

        self.stacked_layout.setCurrentWidget(self.main_widget)

        # Ustawiamy główny layout tego widgetu na stacked_layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.stacked_layout)

    def show_earlier_page(self):
        valid, msg = self.main_form.validate_fields()
        if not valid:
            QMessageBox.warning(self, "Błąd walidacji", msg)
            return
        self.stacked_layout.setCurrentWidget(self.earlier_page)

    def show_main_form(self):
        self.stacked_layout.setCurrentWidget(self.main_widget)

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
