from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from components.PatientSummary import PatientSummary
from components.ResultTable import ResultTable
from components.StyledHeader import StyledHeader
from components.StyledLegend import StyledLegend


class ResultsPage(QWidget):
    def __init__(self, parent=None, examine_id=None, legend_items=None, patient_id=None):
        super().__init__(parent)

        self.background = QPixmap("assets:img/background.png")
        self.scaled_background = self.background
        self.setWindowTitle("Results Page")

        # -----------------------------
        # Główny layout strony
        # -----------------------------
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # -----------------------------
        # Header
        # -----------------------------
        header = StyledHeader("Wyniki")
        main_layout.addWidget(header)

        # Spacer górny - wypycha content w dół
        main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # -----------------------------
        # HBox: tabela po lewej, PatientSummary po prawej
        # -----------------------------
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Tabela wyników
        table_widget = ResultTable(examine_id=examine_id)
        table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(table_widget)

        # PatientSummary
        patient_widget = PatientSummary(patient_id=patient_id)
        patient_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(patient_widget)

        main_layout.addLayout(content_layout)

        # Spacer dolny - wypycha content w górę
        main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # -----------------------------
        # Legenda
        # -----------------------------
        legend_items = legend_items or [
            "Pom. - pominięcia",
            "Zniek. - zniekształcenia",
            "Rot. - rotacje",
            "Przes. - przesunięcia",
            "Dod. - dodatki"
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
