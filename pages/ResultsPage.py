from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from components.PatientSummary import PatientSummary
from components.ResultTable import ResultTable
from components.StyledHeader import StyledHeader
from components.StyledLegend import StyledLegend


class ResultsPage(QWidget):
    def __init__(self, parent=None, examine_id=None, legend_items=None, patient_id=None, summary=None, metrics=None):
        super().__init__(parent)
        print(f"ResultsPage: __init__ started for examine_id={examine_id}")

        # self.setStyleSheet("background-color: transparent;")
        self.background = QPixmap("assets:img/background.png")
        if self.background.isNull():
            print("ResultsPage: WARNING - background image not found!")
            self.setStyleSheet("background-color: white;")
        else:
            self.setStyleSheet("background-color: white;") # Fallback background
        self.scaled_background = self.background
        self.setWindowTitle("Results Page")
        self.summary = summary
        self._metrics = metrics

        # -----------------------------
        # Główny layout strony
        # -----------------------------
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # -----------------------------
        try:
            # Header
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
            print("ResultsPage: creating ResultTable")
            table_widget = ResultTable(examine_id=examine_id, summary=self.summary)
            table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            content_layout.addWidget(table_widget)

            # PatientSummary
            print("ResultsPage: creating PatientSummary")
            patient_widget = PatientSummary(
                patient_id=patient_id,
                metrics=self._metrics
            )
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
        except Exception as e:
            print(f"ResultsPage: CRITICAL ERROR during UI setup: {e}")
            import traceback
            print(traceback.format_exc())

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
        if self.scaled_background and not self.scaled_background.isNull():
            x = (self.width() - self.scaled_background.width()) // 2
            y = (self.height() - self.scaled_background.height()) // 2
            painter.drawPixmap(x, y, self.scaled_background)
        else:
            # Rysujemy białe tło jeśli brak obrazka
            painter.fillRect(self.rect(), Qt.GlobalColor.white)
        super().paintEvent(event)
