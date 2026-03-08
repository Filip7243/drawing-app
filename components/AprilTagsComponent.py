from PyQt6 import QtWidgets, QtGui, QtCore

from components.DrawingCanvas import DrawingCanvas


class AprilTagsComponent(QtWidgets.QWidget):
    def __init__(self, parent=None, num_tags=4, show_canvas=False, show_frame=False):
        super().__init__(parent)

        self.num_tags = num_tags
        self.show_canvas = show_canvas
        self.show_frame = show_frame

        # Lista na dodatkowe widgety do paska (np. przyciski)
        self._frame_widgets = []

        if show_frame:
            # Lista QLabel dla ramki (czarne paski między tagami)
            # Tworzymy 4 paski: góra, dół, lewo, prawo
            self.frame_bars = [QtWidgets.QLabel(self) for _ in range(4)]
            for bar in self.frame_bars:
                bar.setAutoFillBackground(True)
                palette = bar.palette()
                palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("black"))
                bar.setPalette(palette)
                bar.show()
        else:
            self.frame_bars = []

        # Lista QLabel dla tagów
        self.tags = [QtWidgets.QLabel(self) for _ in range(num_tags)]
        for i, tag in enumerate(self.tags):
            tag.setScaledContents(True)
            tag.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            path = f"assets/tag/tag{i}.jpg"  # TODO: to chyba do poprawy
            pixmap = QtGui.QPixmap(path)
            tag.setPixmap(pixmap)
            tag.show()

        if show_canvas:
            self.canvas = DrawingCanvas(self)
            self.canvas.show()
            self.canvas.lower()

    def add_widget_to_frame(self, widget):
        """Dodaje widget do komponentu, który będzie pozycjonowany na ramce."""
        if not self.show_frame:
            return
        widget.setParent(self)
        self._frame_widgets.append(widget)
        widget.show()
        widget.raise_()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        # super().resizeEvent(event)  # Możemy wywołać, ale zazwyczaj niepotrzebne dla QWidget
        w, h = event.size().width(), event.size().height()
        tag_size = int(min(w, h) // self.num_tags)

        # 4 rogi
        self.tags[0].setGeometry(0, 0, tag_size, tag_size)  # lewy górny
        self.tags[1].setGeometry(w - tag_size, 0, tag_size, tag_size)  # prawy górny
        self.tags[2].setGeometry(0, h - tag_size, tag_size, tag_size)  # lewy dolny
        self.tags[3].setGeometry(w - tag_size, h - tag_size, tag_size, tag_size)  # prawy dolny

        if self.num_tags == 6:
            # 2 środkowe (góra i dół)
            self.tags[4].setGeometry((w - tag_size) // 2, 0, tag_size, tag_size)  # środek góra
            self.tags[5].setGeometry((w - tag_size) // 2, h - tag_size, tag_size, tag_size)  # środek dół

        if self.show_canvas:
            # DrawingCanvas zawsze na cały obszar
            self.canvas.setGeometry(0, 0, w, h)
            
        if self.show_frame:
            # Pozycjonujemy czarne paski ramki
            # 0: góra, 1: dół, 2: lewo, 3: prawo
            self.frame_bars[0].setGeometry(tag_size, 0, w - 2 * tag_size, tag_size)
            self.frame_bars[1].setGeometry(tag_size, h - tag_size, w - 2 * tag_size, tag_size)
            self.frame_bars[2].setGeometry(0, tag_size, tag_size, h - 2 * tag_size)
            self.frame_bars[3].setGeometry(w - tag_size, tag_size, tag_size, h - 2 * tag_size)

            for bar in self.frame_bars:
                bar.raise_()

            # Pozycjonowanie przycisku na dolnej ramce (tylko gdy num_tags == 6)
            if self.num_tags == 6 and len(self._frame_widgets) >= 1:
                # Zakładamy kolejność: done jest ostatni lub jedyny
                done_btn = self._frame_widgets[-1]

                # Pozycjonowanie przycisku "DALEJ" pomiędzy 2 a 3 tagiem (środkowy i prawy)
                # Środkowy tag kończy się na (w - tag_size) // 2 + tag_size
                # Prawy tag zaczyna się na w - tag_size
                space2_start = (w - tag_size) // 2 + tag_size
                space2_end = w - tag_size
                space2_center = (space2_start + space2_end) // 2
                
                done_btn.setFixedHeight(max(10, tag_size - 10))
                done_btn.setFixedWidth(max(10, min(space2_end - space2_start - 20, 500)))
                done_btn.adjustSize()
                done_btn.move(space2_center - done_btn.width() // 2, h - tag_size + (tag_size - done_btn.height()) // 2)

                for widget in self._frame_widgets:
                    widget.raise_()

            # Tagi na wierzchu
            for tag in self.tags:
                tag.raise_()
