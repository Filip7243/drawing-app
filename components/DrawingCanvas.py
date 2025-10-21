from PyQt6 import QtWidgets, QtGui, QtCore

from PyQt6 import QtWidgets, QtGui, QtCore


class DrawingCanvas(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StaticContents)
        self.setMouseTracking(True)

        # Obraz, na którym rysujemy
        self.image = QtGui.QImage(self.size(), QtGui.QImage.Format.Format_RGB32)
        self.image.fill(QtGui.QColor("#FFEDCC"))

        # Aktualna linia
        self.last_point = None
        self.pen_color = QtGui.QColor("black")
        self.pen_width = 2

    def setPenColor(self, color):
        self.pen_color = QtGui.QColor(color)

    def setPenWidth(self, width):
        self.pen_width = width

    def resizeEvent(self, event):
        # Powiększ obraz przy zmianie rozmiaru widgetu
        if self.width() > self.image.width() or self.height() > self.image.height():
            new_image = QtGui.QImage(self.size(), QtGui.QImage.Format.Format_RGB32)
            new_image.fill(QtGui.QColor("#FFEDCC"))
            painter = QtGui.QPainter(new_image)
            painter.drawImage(0, 0, self.image)
            painter.end()
            self.image = new_image
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(self.rect(), self.image, self.image.rect())

    def _mapEventToImage(self, pos):
        """
        Mapuje pozycję z eventu (współrzędne widgetu) na współrzędne obrazu.
        Uwzględnia skalowanie, jeśli obraz ma inny rozmiar niż widget.
        """
        widget_rect = self.rect()
        image_rect = self.image.rect()

        # Oblicz skalę
        scale_x = image_rect.width() / widget_rect.width() if widget_rect.width() > 0 else 1
        scale_y = image_rect.height() / widget_rect.height() if widget_rect.height() > 0 else 1

        # Mapuj pozycję
        x = int(pos.x() * scale_x)
        y = int(pos.y() * scale_y)

        # Ogranicz do granic obrazu
        x = max(0, min(x, image_rect.width() - 1))
        y = max(0, min(y, image_rect.height() - 1))

        return QtCore.QPoint(x, y)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.last_point = self._mapEventToImage(event.position())

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() & QtCore.Qt.MouseButton.LeftButton and self.last_point is not None:
            painter = QtGui.QPainter(self.image)
            pen = QtGui.QPen(self.pen_color, self.pen_width, QtCore.Qt.PenStyle.SolidLine,
                             QtCore.Qt.PenCapStyle.RoundCap, QtCore.Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)

            current_point = self._mapEventToImage(event.position())
            painter.drawLine(self.last_point, current_point)
            painter.end()

            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.last_point = None

    def tabletEvent(self, event: QtGui.QTabletEvent):
        """
        Obsługa rysika/tabletu graficznego z uwzględnieniem nacisku
        """
        pressure = event.pressure()  # 0.0 - 1.0

        # Dynamiczna grubość na podstawie nacisku
        if pressure > 0:
            self.pen_width = max(1, int(pressure * 10))

        # Mapuj pozycję rysika
        mapped_pos = self._mapEventToImage(event.position())

        if event.type() == QtCore.QEvent.Type.TabletPress:
            self.last_point = mapped_pos
            event.accept()

        elif event.type() == QtCore.QEvent.Type.TabletMove:
            if self.last_point is not None:
                painter = QtGui.QPainter(self.image)
                pen = QtGui.QPen(self.pen_color, self.pen_width, QtCore.Qt.PenStyle.SolidLine,
                                 QtCore.Qt.PenCapStyle.RoundCap, QtCore.Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                painter.drawLine(self.last_point, mapped_pos)
                painter.end()

                self.last_point = mapped_pos
                self.update()
            event.accept()

        elif event.type() == QtCore.QEvent.Type.TabletRelease:
            self.last_point = None
            event.accept()
