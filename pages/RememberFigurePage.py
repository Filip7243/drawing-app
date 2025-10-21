from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter

from components.AprilTagsComponent import AprilTagsComponent
from components.StyledHeader import StyledHeader
from components.TimeBar import TimeBar


class RememberFigurePage(QWidget):
    def __init__(self,
                 bg_path="assets:img/figures/tutorial_figure.png",
                 parent=None):
        super().__init__(parent)
        self.background = QPixmap(bg_path)
        self.scaled_background = self.background
        self.setWindowTitle("Remember Figure Page")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)  # brak marginesów

        time_bar = TimeBar(max_time=10)
        main_layout.addWidget(time_bar)

        header = StyledHeader("Zapamiętaj rysunek")
        main_layout.addWidget(header)

        # TODO: porozmawiać jeszcze o tych AprilTags, najlepiej
        # TODO: będzie to przetestować i sprawdzić ile tych tagów
        # TODO: i jaka wielkość
        april_tags = AprilTagsComponent(num_tags=4)
        main_layout.addWidget(april_tags)

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
