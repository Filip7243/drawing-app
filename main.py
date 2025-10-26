import os
import sys
from pathlib import Path

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QApplication

from controllers.FlowController import FlowController
from pages.AudioStepPage import AudioStepPage
from pages.DrawingPage import DrawingPage
from pages.MainFormPage import MainFormPage
from pages.RememberFigurePage import RememberFigurePage

from db.database_manager_singleton import get_db

CURRENT_DIRECTORY = Path(__file__).resolve().parent


def step_audio(audio_file: str):
    def _factory():
        page = AudioStepPage(audio=audio_file)
        return page

    return _factory


def step_remember(is_tutorial: bool, bg: str = "assets:img/figures/tutorial_figure_white.png"):
    def _factory():
        page = RememberFigurePage(bg_path=bg, is_tutorial=is_tutorial)
        return page

    return _factory


def step_draw(is_tutorial: bool):
    def _factory():
        page = DrawingPage(is_tutorial=is_tutorial)
        return page

    return _factory


TUTORIAL_SEQUENCE = [
    step_audio("01_powitanie.wav"),
    step_audio("02_zapamietaj_rysunek_przedmowa.wav"),
    step_remember(is_tutorial=True),
    step_draw(is_tutorial=True),
    step_audio("07_koniec_samouczka.wav"),
]

TEST_SEQUENCE = [
    step_audio("03_zapamietaj_rysunek.wav"),
    step_remember(is_tutorial=False),
    step_draw(is_tutorial=False),
]


def main():
    # app = QApplication(sys.argv)

    QDir.addSearchPath("assets", os.fspath(CURRENT_DIRECTORY / "assets"))

    db = get_db()
    db.close()
    # window = MainFormPage()
    # window.showMaximized()
    # controller = FlowController()
    # controller.set_sequence(TUTORIAL_SEQUENCE)
    # controller.set_loop(True)
    #
    # def on_tutorial_complete():
    #     controller.set_loop(False)
    #     controller.set_on_complete(None)
    #     controller.set_sequence(TEST_SEQUENCE)
    #     controller.start()
    #
    # controller.set_on_complete(on_tutorial_complete)
    # controller.start()

    # sys.exit(app.exec())


if __name__ == "__main__":
    main()
