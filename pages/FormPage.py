from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QWidget


class FormPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background = QPixmap("assets:img/background.png")
        self.scaled_background = self.background  # bufor
        self.setWindowTitle("Form Page")

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
            # Oblicz offset do wyśrodkowania
            x = (self.width() - self.scaled_background.width()) // 2
            y = (self.height() - self.scaled_background.height()) // 2
            painter.drawPixmap(x, y, self.scaled_background)
        super().paintEvent(event)