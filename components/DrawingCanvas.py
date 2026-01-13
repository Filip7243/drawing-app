from PyQt6 import QtWidgets, QtGui, QtCore
from time import perf_counter


class DrawingCanvas(QtWidgets.QWidget):
    firstStroke = QtCore.pyqtSignal()
    strokeStarted = QtCore.pyqtSignal()
    strokeFinished = QtCore.pyqtSignal()
    strokeDataCollected = QtCore.pyqtSignal(dict)
    undoClicked = QtCore.pyqtSignal()
    redoClicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StaticContents)
        self.setMouseTracking(True)

        self.image = None
        self.last_point = None
        self.pen_color = QtGui.QColor("black")
        self.pen_width = 2
        self._first_stroke_recorded = False
        self._undo_stack = []
        self._redo_stack = []
        self._max_undo_steps = 50

        self._current_stroke_points = []
        self._current_stroke_overdraw_count = 0
        self._current_stroke_total_count = 0
        self._current_stroke_overdraw_cells = {}
        self._grid_size = 40

    def _save_state(self):
        """Zapisuje aktualny obraz na stosie undo."""
        if self.image is not None:
            self._undo_stack.append(self.image.copy())
            if len(self._undo_stack) > self._max_undo_steps:
                self._undo_stack.pop(0)
            self._redo_stack.clear()

    def undo(self):
        """Cofa ostatnią zmianę."""
        if not self._undo_stack:
            return

        if self.image is not None:
            self._redo_stack.append(self.image.copy())

        self.image = self._undo_stack.pop()
        self.undoClicked.emit()
        self.update()

    def redo(self):
        """Ponawia ostatnio cofniętą zmianę."""
        if not self._redo_stack:
            return

        if self.image is not None:
            self._undo_stack.append(self.image.copy())

        self.image = self._redo_stack.pop()
        self.redoClicked.emit()
        self.update()

    def setPenColor(self, color):
        self.pen_color = QtGui.QColor(color)

    def setPenWidth(self, width):
        self.pen_width = width

    def resizeEvent(self, event):
        """Tworzy lub powiększa QImage przy zmianie rozmiaru widgetu."""
        new_size = self.size()

        if self.image is None:
            # Tworzymy pierwszy raz
            self.image = QtGui.QImage(new_size, QtGui.QImage.Format.Format_RGB32)
            self.image.fill(QtGui.QColor("#FFFFFF"))
        elif new_size.width() > self.image.width() or new_size.height() > self.image.height():
            # Powiększamy istniejący obraz
            new_image = QtGui.QImage(new_size, QtGui.QImage.Format.Format_RGB32)
            new_image.fill(QtGui.QColor("#FFFFFF"))
            painter = QtGui.QPainter(new_image)
            painter.drawImage(0, 0, self.image)
            painter.end()
            self.image = new_image

        super().resizeEvent(event)

    def paintEvent(self, event):
        """Rysuje aktualny obraz na ekranie."""
        if self.image is None:
            return
        painter = QtGui.QPainter(self)
        painter.drawImage(self.rect(), self.image, self.image.rect())

    def _mapEventToImage(self, pos):
        """Mapuje współrzędne eventu na współrzędne obrazu."""
        if self.image is None:
            return QtCore.QPoint(0, 0)

        widget_rect = self.rect()
        image_rect = self.image.rect()
        scale_x = image_rect.width() / widget_rect.width() if widget_rect.width() > 0 else 1
        scale_y = image_rect.height() / widget_rect.height() if widget_rect.height() > 0 else 1

        x = int(pos.x() * scale_x)
        y = int(pos.y() * scale_y)
        x = max(0, min(x, image_rect.width() - 1))
        y = max(0, min(y, image_rect.height() - 1))
        return QtCore.QPoint(x, y)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """
         Za każdym razem, gdy rysujemy, zapisujemy stan obrazka, to co było aktualnie namalowane na stos undo,
         współrzędne rysowanej linii wraz z timestamp, kiedy zostały namalowane,
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self.image is not None:
            self._save_state()

            # Emitujemy firstStroke, żeby złapać moment pierwszego dotknięcia ekranu po wyświetleniu canvas do rysowania
            if not self._first_stroke_recorded:
                self._first_stroke_recorded = True
                self.firstStroke.emit()

            # Emitujemy event, który przechwytujemy w FlowController.py
            self.strokeStarted.emit()

            pos = self._mapEventToImage(event.position())
            self.last_point = pos

            # Zapisujemy pixel (timestamp, x, y) - przypadek, gdy zostanie narysowana kropka
            self._current_stroke_points = [(perf_counter(), pos.x(), pos.y())]
            self._current_stroke_overdraw_count = 0
            self._current_stroke_total_count = 0
            self._current_stroke_overdraw_cells = {}

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if (event.buttons() & QtCore.Qt.MouseButton.LeftButton
                and self.last_point is not None
                and self.image is not None):
            current_point = self._mapEventToImage(event.position())

            # Detekcja nadrysowania ("rysowania w miejscu")
            pixel_color = QtGui.QColor(self.image.pixel(current_point))
            if pixel_color.rgb() != QtGui.QColor("#FFFFFF").rgb():
                self._current_stroke_overdraw_count += 1

                # Zapisywanie nadrysowania w komórce
                cx, cy = current_point.x() // self._grid_size, current_point.y() // self._grid_size
                self._current_stroke_overdraw_cells[(cx, cy)] = self._current_stroke_overdraw_cells.get((cx, cy), 0) + 1

            self._current_stroke_total_count += 1
            self._current_stroke_points.append((perf_counter(), current_point.x(), current_point.y()))

            painter = QtGui.QPainter(self.image)
            pen = QtGui.QPen(self.pen_color, self.pen_width,
                             QtCore.Qt.PenStyle.SolidLine,
                             QtCore.Qt.PenCapStyle.RoundCap,
                             QtCore.Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.last_point, current_point)
            painter.end()

            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        """Wywoływane po zakończeniu rysowania linii"""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._emit_stroke_data()

            # Event łapany w FlowController.py
            self.strokeFinished.emit()
            self.last_point = None

    def _emit_stroke_data(self):
        """Oblicza i emituje metryki dla zakończonej kreski."""
        if not self._current_stroke_points:
            return

        # Obliczanie długości ścieżki i zmian kierunku
        path_length = 0
        direction_changes = 0
        t0, x0, y0 = self._current_stroke_points[0]
        min_x = max_x = x0
        min_y = max_y = y0

        import math

        last_angle = None
        # Próg zmiany kierunku (w stopniach) - np. 45 stopni. Zgodnie z wytycznymi Pani psycholog.
        ANGLE_THRESHOLD = 45

        for i in range(1, len(self._current_stroke_points)):
            t1, x1, y1 = self._current_stroke_points[i - 1]
            t2, x2, y2 = self._current_stroke_points[i]

            # Tworzymy wektor
            dx = x2 - x1  # Przesunięcie w osi X
            dy = y2 - y1  # Przesunięcie w osi Y

            # Wyliczamy odległość pomiędzy punktami
            dist = (dx ** 2 + dy ** 2) ** 0.5
            path_length += dist

            # Wyliczamy kąt pomiędzy wektorami [-pi, pi] aby wykryć nagłe zmiany kirunku podczas rysowania
            if dist > 2:  # Ignorujemy bardzo małe ruchy (może to być szum)
                current_angle = math.atan2(dy, dx)
                if last_angle is not None:
                    diff = abs(math.degrees(current_angle - last_angle))
                    if diff > 180:
                        diff = 360 - diff
                    if diff > ANGLE_THRESHOLD:
                        print(f"DIRECTION CHAGED DIFF: {diff}")
                        direction_changes += 1
                last_angle = current_angle

            min_x = min(min_x, x2)
            max_x = max(max_x, x2)
            min_y = min(min_y, y2)
            max_y = max(max_y, y2)

        # Pole powierzchni rysunku (nie mylić z polem powierzchni do rysowania).
        bbox_area = (max_x - min_x) * (max_y - min_y)

        data = {
            'overdrawn_pixels': self._current_stroke_overdraw_count,
            'total_pixels': self._current_stroke_total_count,
            'points': self._current_stroke_points,
            'path_length': path_length,
            'bounding_box_area': bbox_area,
            'direction_changes': direction_changes,
            'overdraw_cells': self._current_stroke_overdraw_cells
        }
        # Event przechwytywany w FlowController.py
        self.strokeDataCollected.emit(data)
        self._current_stroke_points = []

    def tabletEvent(self, event: QtGui.QTabletEvent):
        """Obsługa rysika z naciskiem."""
        if self.image is None:
            return

        pressure = event.pressure()
        if pressure > 0:
            self.pen_width = max(1, int(pressure * 10))

        mapped_pos = self._mapEventToImage(event.position())
        if event.type() == QtCore.QEvent.Type.TabletPress:
            self._save_state()
            if not self._first_stroke_recorded:
                self._first_stroke_recorded = True
                self.firstStroke.emit()
            self.strokeStarted.emit()
            self.last_point = mapped_pos
            # Zapisujemy pixel (timestamp, x, y) - przypadek, gdy zostanie narysowana kropka
            self._current_stroke_points = [(perf_counter(), mapped_pos.x(), mapped_pos.y())]
            self._current_stroke_overdraw_count = 0
            self._current_stroke_total_count = 0
            self._current_stroke_overdraw_cells = {}
            event.accept()

        elif event.type() == QtCore.QEvent.Type.TabletMove and self.last_point is not None:
            # Detekcja nadrysowania ("rysowania w miejscu")
            pixel_color = QtGui.QColor(self.image.pixel(mapped_pos))
            if pixel_color.rgb() != QtGui.QColor("#FFFFFF").rgb():
                self._current_stroke_overdraw_count += 1

                # Zapisywanie nadrysowania w komórce
                cx, cy = mapped_pos.x() // self._grid_size, mapped_pos.y() // self._grid_size
                self._current_stroke_overdraw_cells[(cx, cy)] = self._current_stroke_overdraw_cells.get((cx, cy), 0) + 1

            self._current_stroke_total_count += 1
            self._current_stroke_points.append((perf_counter(), mapped_pos.x(), mapped_pos.y()))

            painter = QtGui.QPainter(self.image)
            pen = QtGui.QPen(self.pen_color, self.pen_width,
                             QtCore.Qt.PenStyle.SolidLine,
                             QtCore.Qt.PenCapStyle.RoundCap,
                             QtCore.Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.last_point, mapped_pos)
            painter.end()

            self.last_point = mapped_pos
            self.update()
            event.accept()

        elif event.type() == QtCore.QEvent.Type.TabletRelease:
            self._emit_stroke_data()

            # Event łapany w FlowController.py
            self.strokeFinished.emit()
            self.last_point = None
            event.accept()

    def export_as_image(self) -> QtGui.QImage:
        """Zwraca kopię aktualnego obrazu jako QImage."""
        if self.image is None:
            return QtGui.QImage()
        return self.image.copy()
