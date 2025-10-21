from PyQt6 import QtWidgets, QtGui, QtCore

from components.DrawingCanvas import DrawingCanvas


class AprilTagsComponent(QtWidgets.QWidget):
    def __init__(self, parent=None, num_tags=4, show_canvas=False):
        super().__init__(parent)

        self.num_tags = num_tags
        self.show_canvs = show_canvas

        # Lista QLabel dla tagów
        self.tags = [QtWidgets.QLabel(self) for _ in range(num_tags)]
        for i, tag in enumerate(self.tags):
            tag.setScaledContents(True)
            tag.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            path = f"assets/tag/tag{i}.jpg"
            pixmap = QtGui.QPixmap(path)
            tag.setPixmap(pixmap)
            tag.show()

        if show_canvas:
            self.canvas = DrawingCanvas(self)
            self.canvas.show()
            self.canvas.lower()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)
        w, h = self.width(), self.height()
        tag_size = min(w, h) // self.num_tags

        # 4 rogi
        self.tags[0].setGeometry(0, 0, tag_size, tag_size)  # lewy górny
        self.tags[1].setGeometry(w - tag_size, 0, tag_size, tag_size)  # prawy górny
        self.tags[2].setGeometry(0, h - tag_size, tag_size, tag_size)  # lewy dolny
        self.tags[3].setGeometry(w - tag_size, h - tag_size, tag_size, tag_size)  # prawy dolny

        if self.num_tags == 6:
            # 2 środkowe (góra i dół)
            self.tags[4].setGeometry((w - tag_size) // 2, 0, tag_size, tag_size)  # środek góra
            self.tags[5].setGeometry((w - tag_size) // 2, h - tag_size, tag_size, tag_size)  # środek dół

        if self.show_canvs:
            self.canvas.setGeometry(0, 0, w, h)
            # Tagi na wierzchu
            for tag in self.tags:
                tag.raise_()
            # KOD KTORY RYSUJE CANVAS POZA APRIL TAGS
            # left = tag_size
            # top = tag_size
            # right = w - tag_size
            # bottom = h - tag_size
            # self.canvas.setGeometry(left, top, right - left, bottom - top)
