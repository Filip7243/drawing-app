import os
import sys
from pathlib import Path

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QApplication

from controllers.FlowController import FlowController
from controllers.TestMetrics import TestMetrics
from db.models import TestMetaData
from pages.AudioStepPage import AudioStepPage
from pages.DrawingPage import DrawingPage
from pages.MainFormPage import MainFormPage
from pages.RememberFigurePage import RememberFigurePage
from pages.ResultsPage import ResultsPage

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


def step_form():
    def _factory():
        page = MainFormPage()
        return page

    return _factory


TUTORIAL_SEQUENCE = [
    # step_form(),
    # step_audio("01_powitanie.wav"),
    # step_audio("02_zapamietaj_rysunek_przedmowa.wav"),
    # step_remember(is_tutorial=True),
    # step_draw(is_tutorial=True),
    step_audio("07_koniec_samouczka.wav"),
]

TEST_SEQUENCE = [
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_1.png"),
    step_draw(is_tutorial=False),
    # step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_2.png"),
    # step_draw(is_tutorial=False),
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_3.png"),
    step_draw(is_tutorial=False),
    # step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_4.png"),
    # step_draw(is_tutorial=False),
    # step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_5.png"),
    # step_draw(is_tutorial=False),
    # step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_6.png"),
    # step_draw(is_tutorial=False),
    # step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_7.png"),
    # step_draw(is_tutorial=False),
    # step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_8.png"),
    # step_draw(is_tutorial=False),
    # step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_9.png"),
    # step_draw(is_tutorial=False),
    # step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_10.png"),
    # step_draw(is_tutorial=False),
]


# def main():
#     # app = QApplication(sys.argv)
#
#     QDir.addSearchPath("assets", os.fspath(CURRENT_DIRECTORY / "assets"))
#
#     db = get_db()
#     db.close()
#     window = MainFormPage()
#     # window.showMaximized()
#     # controller = FlowController()
#     # controller.set_sequence(TUTORIAL_SEQUENCE)
#     # controller.set_loop(True)
#     #
#     # def on_tutorial_complete():
#     #     controller.set_loop(False)
#     #     controller.set_on_complete(None)
#     #     controller.set_sequence(TEST_SEQUENCE)
#     #     controller.start()
#     #
#     # controller.set_on_complete(on_tutorial_complete)
#     # controller.start()
#
#     # sys.exit(app.exec())

def main():
    app = QApplication(sys.argv)

    QDir.addSearchPath("assets", os.fspath(CURRENT_DIRECTORY / "assets"))

    table_data = [
        {"rys": 1, "poprawne": True, "bledy": [1, 0, 0, 0, 1], "czas": 20},
        {"rys": 2, "poprawne": False, "bledy": [0, 1, 2, 0, 0], "czas": 20},
        {"rys": 3, "poprawne": True, "bledy": [0, 0, 1, 0, 0], "czas": 20},
        {"rys": 4, "poprawne": True, "bledy": [0, 0, 1, 0, 0], "czas": 20},
        {"rys": 5, "poprawne": True, "bledy": [0, 0, 1, 0, 0], "czas": 20},
        {"rys": 6, "poprawne": True, "bledy": [0, 0, 1, 0, 0], "czas": 20},
        {"rys": 7, "poprawne": True, "bledy": [0, 0, 1, 0, 0], "czas": 20},
        {"rys": 8, "poprawne": True, "bledy": [0, 0, 1, 0, 0], "czas": 20},
        {"rys": 9, "poprawne": True, "bledy": [0, 0, 1, 0, 0], "czas": 20},
        {"rys": 10, "poprawne": True, "bledy": [0, 0, 1, 0, 0], "czas": 20},
    ]
    patient_data = {
        "pacjent": "P0001",
        "plec": "Mężczyzna",
        "wiek": "7 lat",
        "reka": "Prawa",
        "wada": "-1P, +1L",
        "uwagi": "Badanie wzroku kontrolne",
        "funkcje": "W normie"
    }
    earlier_examines_data = [
        {
            "data": "2025-10-30",
            "bledne": 2,
            "poprawne": 8,
            "czas_sredni": 1.25,
            "czas_cal": 12.5,
            "typy_bledow": [1, 0, 2, 0, 1],
            "profil": "W normie",
            "uwagi": "Brak uwag"
        },
        {
            "data": "2025-10-29",
            "bledne": 3,
            "poprawne": 7,
            "czas_sredni": 1.4,
            "czas_cal": 14.0,
            "typy_bledow": [0, 1, 1, 2, 0],
            "profil": "Poniżej normy",
            "uwagi": "Wymaga dalszej obserwacji"
        }
    ]

    # repo = InitRepository()
    # repo.createTypes()
    # repo.createPatientTable()
    # repo.createCommentsTable()
    # repo.createPatientDegrees()
    # repo.createExamineTable()
    # repo.createImageTable()
    # repo.createExamineReasonsTable()
    # repo.createFailureTable()
    # window = MainFormPage()
    # window.showMaximized()
    # window = PatientSummary({
    #     "pacjent": "P0001",
    #     "plec": "Mężczyzna",
    #     "wiek": "7 lat",
    #     "reka": "Prawa",
    #     "wada": "-1P, +1L",
    #     "uwagi": "Badanie wzroku kontrolne",
    #     "funkcje": "W normie"
    # })

    # window = StyledLegend([
    #     "Pom. - pominięcia",
    #     "Zniek. - zniekształcenia",
    #     "Rot. - rotacje",
    #     "Przes. - przesunięcia",
    #     "Dod. - dodatki"
    # ])

    # window = ResultsPage(table_data=table_data, patient_data=patient_data)

    # window = EarlierExaminesPage(table_data=earlier_examines_data)
    # window.showMaximized()

    ## SEKWENCJA

    # inicjalizacja bazy
    # db = get_db()
    # db.close()

    metrics = TestMetrics()

    controller = FlowController()
    controller.set_loop(True)
    controller.set_sequence(TUTORIAL_SEQUENCE)
    controller.set_metrics(metrics)
    # metrics.start_test()

    main_page = MainFormPage()
    main_page.showMaximized()

    # Po ukończeniu tutoriala przejdź do testu
    def on_tutorial_complete():
        controller.set_loop(False)
        controller.set_on_complete(None)
        controller.set_sequence(TEST_SEQUENCE)
        controller.set_test_mode(True)
        metrics.start_test()

        def on_test_complete():
            summary = metrics.end_test()
            print("SUMMARY:", summary)
            controller.set_test_mode(False)

            meta = main_page.main_form.get_test_metadata()
            print("RESULTS PAGE WITH ID: ", meta.patient_id)
            results_page = ResultsPage(examine_id=meta.examine_id, patient_id=meta.patient_id)
            controller.stack.addWidget(results_page)
            controller.stack.setCurrentWidget(results_page)

        controller.set_on_complete(on_test_complete)
        controller.start()

    controller.set_on_complete(on_tutorial_complete)

    # controller.start()

    def on_start_requested():
        meta = main_page.main_form.get_test_metadata()
        metrics.test_meta_data(TestMetaData(examine_id=meta.examine_id, patient_id=meta.patient_id))
        main_page.close()
        controller.start()

    # Nasłuchiwanie kliknięcia "Rozpocznij" w formularzu głównym
    main_page.startRequested.connect(on_start_requested)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
