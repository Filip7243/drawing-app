from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter

from components.AprilTagsComponent import AprilTagsComponent
from components.StyledHeader import StyledHeader
from components.TimeBar import TimeBar
from pages.DrawingPage import DrawingPage


class RememberFigurePage(QWidget):
    def __init__(self,
                 bg_path="assets:img/figures/tutorial_figure.png",
                 parent=None):
        super().__init__(parent)
        self.background = QPixmap(bg_path)
        self.scaled_background = self.background
        self.setWindowTitle("Remember Figure Page")

        self.timer = QTimer(self)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)  # brak marginesów

        self.time_bar = TimeBar(max_time=3)
        main_layout.addWidget(self.time_bar)

        header = StyledHeader("Zapamiętaj rysunek")
        main_layout.addWidget(header)

        # TODO: porozmawiać jeszcze o tych AprilTags, najlepiej
        # TODO: będzie to przetestować i sprawdzić ile tych tagów
        # TODO: i jaka wielkość
        april_tags = AprilTagsComponent(num_tags=4)
        main_layout.addWidget(april_tags)

        self.setLayout(main_layout)

    def showEvent(self, event):
        """Uruchamia timer TimeBar po wyrenderowaniu okna"""
        super().showEvent(event)
        QTimer.singleShot(0, self.start_time_bar)

    def start_time_bar(self):
        """Funkcja startująca odliczanie TimeBar"""
        self.time_bar.setTime(self.time_bar.max_time)
        self.timer.timeout.connect(self.update_time_bar)
        self.timer.start(1000)  # zmienia stan timera co sekundę

    def update_time_bar(self):
        if self.time_bar.current_time > 0:
            self.time_bar.setTime(self.time_bar.current_time - 1)
        else:
            self.timer.stop()

            # Po widoku z zapamiętywaniem przechodzimy do rysowania
            self.drawing_page = DrawingPage()
            self.drawing_page.show()
            self.hide()

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
