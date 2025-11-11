from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from components.EarlierExaminesTable import EarlierExaminesTable
from components.StyledHeader import StyledHeader
from components.StyledLegend import StyledLegend


class EarlierExaminesPage(QWidget):
    backRequested = pyqtSignal()

    def __init__(self, parent=None, table_data=None, legend_items=None):
        super().__init__(parent)

        self.background = QPixmap("assets:img/background.png")
        self.scaled_background = self.background
        self.setWindowTitle("Results Page")

        print("table_data: ", table_data)

        # -----------------------------
        # Główny layout strony
        # -----------------------------
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # -----------------------------
        # Header
        # -----------------------------
        self.header = StyledHeader("Pacjent P0001", show_back_button=True)
        main_layout.addWidget(self.header)

        self.header.back_button.clicked.connect(self.backRequested.emit)

        # Spacer górny - wypycha content w dół
        main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # -----------------------------
        # HBox: tabela po lewej, PatientSummary po prawej
        # -----------------------------
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Tabela wyników
        table_widget = EarlierExaminesTable(data=table_data)
        table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(table_widget)

        main_layout.addLayout(content_layout)

        # Spacer dolny - wypycha content w górę
        main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # -----------------------------
        # Legenda
        # -----------------------------
        legend_items = legend_items or [
            "Śr. - Średni czas spędzony na rysowaniu jednego wzoru",
            "Cał. - Całościowy czas testu (rysowania)"
        ]
        legend = StyledLegend(items=legend_items)
        legend.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(legend, alignment=Qt.AlignmentFlag.AlignCenter)

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
