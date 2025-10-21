from PyQt6 import QtCore, QtGui, QtWidgets


class TimeBar(QtWidgets.QWidget):
    def __init__(self, max_time=100, color="#EEB14C", height=10, parent=None):
        super().__init__(parent)
        self.max_time = max_time  # maksymalny czas
        self.current_time = max_time  # aktualny czas = max_time, bo zaczynamy odliczanie od końca do 0
        self.color = color
        self.setFixedHeight(height)
        self.setMinimumWidth(200)

    def setTime(self, time_value):
        """Ustawia aktualny czas"""
        self.current_time = min(max(time_value, 0), self.max_time)
        self.update()  # wymuś przerysowanie

    def setMaxTime(self, max_time):
        """Ustawia maksymalny czas"""
        self.max_time = max_time
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # tło paska
        rect = self.rect()
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#F2DBB5")))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRect(rect)

        # wypełnienie paska
        if self.max_time > 0:
            fill_width = int((self.current_time / self.max_time) * rect.width())
        else:
            fill_width = 0

        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.color)))
        painter.drawRect(0, 0, fill_width, rect.height())

        painter.end()

#
# # --- Przykład użycia ---
# if __name__ == "__main__":
#     import sys
#
#     app = QtWidgets.QApplication(sys.argv)
#
#     window = QtWidgets.QWidget()
#     layout = QtWidgets.QVBoxLayout(window)
#
#     time_bar = TimeBar(max_time=10)  # np. 60 sekund
#     layout.addWidget(time_bar)
#
#     window.show()
#
#
#     # Symulacja upływu czasu
#     def update_bar():
#         if time_bar.current_time > 0:
#             time_bar.setTime(time_bar.current_time - 1)
#         else:
#             timer.stop()
#
#
#     timer = QtCore.QTimer()
#     timer.timeout.connect(update_bar)
#     timer.start(1000)  # co 1 sekundę
#
#     sys.exit(app.exec())
