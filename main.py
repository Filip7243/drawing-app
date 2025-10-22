import os
import sys
from pathlib import Path

from PyQt6.QtCore import QDir, Qt
from PyQt6.QtWidgets import QApplication

from pages.RememberFigurePage import RememberFigurePage

CURRENT_DIRECTORY = Path(__file__).resolve().parent


def main():
    app = QApplication(sys.argv)

    QDir.addSearchPath("assets", os.fspath(CURRENT_DIRECTORY / "assets"))

    # window = DrawingPage()
    # window = MainFormPage()
    window = RememberFigurePage(is_tutorial=True)
    window.start()
    window.showMaximized()
    window.setWindowFlag(Qt.WindowType.Window)  # zwykłe okno
    window.show()  # pokazujemy okno w określonym rozmiarze

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
