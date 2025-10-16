import os
import sys
from pathlib import Path

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QApplication

from pages.FormPage import FormPage

CURRENT_DIRECTORY = Path(__file__).resolve().parent


def main():
    app = QApplication(sys.argv)

    QDir.addSearchPath("assets", os.fspath(CURRENT_DIRECTORY / "assets"))

    window = FormPage()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
