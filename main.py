import os
import sys
from pathlib import Path

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QApplication
from mypyc.crash import catch_errors

from controllers.FlowController import FlowController
from controllers.TestMetrics import TestMetrics
from db.models import TestMetaData
from pages.AudioStepPage import AudioStepPage
from pages.DrawingPage import DrawingPage
from pages.MainFormPage import MainFormPage
from pages.RememberFigurePage import RememberFigurePage
from pages.ResultsPage import ResultsPage
from PyQt6.QtGui import QGuiApplication

CURRENT_DIRECTORY = Path(__file__).resolve().parent


def step_audio(audio_file: str):
    def _factory():
        page = AudioStepPage(audio=audio_file)
        return page

    return _factory


def step_remember(is_tutorial: bool, bg: str = "assets:img/figures/tutorial_figure_white.png", audio: str = None):
    def _factory():
        page = RememberFigurePage(bg_path=bg, is_tutorial=is_tutorial, audio=audio)
        return page

    return _factory


def step_draw(is_tutorial: bool, audio: str = None):
    def _factory():
        page = DrawingPage(is_tutorial=is_tutorial, audio=audio)
        return page

    return _factory


def step_form():
    def _factory():
        page = MainFormPage()
        return page

    return _factory


TUTORIAL_SEQUENCE = [
    # step_form(),
    step_audio("01_powitanie (2).wav"),
    step_audio("02_zapamietaj_rysunek_przedmowa (2).wav"),
    step_remember(is_tutorial=True, audio="03_zapamietaj_rysunek (2).wav"),
    step_draw(is_tutorial=True, audio="05_odwzoruj_rysunek (2).wav"),
    step_audio("07_koniec_samouczka (2).wav"),
]

TEST_SEQUENCE = [
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_1.svg"),
    step_draw(is_tutorial=False),
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_2.svg"),
    step_draw(is_tutorial=False),
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_3.svg"),
    step_draw(is_tutorial=False),
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_4.svg"),
    step_draw(is_tutorial=False),
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_5.svg"),
    step_draw(is_tutorial=False),
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_6.svg"),
    step_draw(is_tutorial=False),
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_7.svg"),
    step_draw(is_tutorial=False),
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_8.svg"),
    step_draw(is_tutorial=False),
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_9.svg"),
    step_draw(is_tutorial=False),
    step_remember(is_tutorial=False, bg="assets:img/figures/bvrt_c_10.svg"),
    step_draw(is_tutorial=False),
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
    # app.setStyleSheet("background-color: white;")

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
    metrics.connect_pupil()

    # Rozłącz Pupil przy zamykaniu aplikacji (np. krzyżykiem)
    app.aboutToQuit.connect(metrics.disconnect_pupil)

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

        def on_test_complete():
            print("on_test_complete: started")
            summary = metrics.end_test()
            controller.set_test_mode(False)

            meta = main_page.main_form.get_test_metadata()
            print(f"on_test_complete: meta found: {meta}")
            results_page = ResultsPage(
                examine_id=meta.examine_id, 
                patient_id=meta.patient_id, 
                summary=summary,
                metrics=metrics
            )
            print(f"on_test_complete: ResultsPage created, visibility={results_page.isVisible()}")
            
            # Pobieramy listę wszystkich ekranów
            screens = QGuiApplication.screens()
            
            # Logika wyboru ekranu lekarza (powrót na ekran 0):
            # Zawsze celujemy w ekran główny (indeks 0).
            target_screen = screens[0]
            print(f"DEBUG: Powrót na ekran lekarza: {target_screen.name()} | Geometry: {target_screen.geometry()}")
            
            # Tworzymy nowe okno dla wyników zamiast dodawać do stacka, 
            # który mógł zostać zamknięty lub być w dziwnym stanie
            # Przypisujemy do atrybutu, aby uniknąć GC
            controller.results_page = results_page
            
            # Przenosimy okno na wybrany ekran przed wyświetleniem
            results_page.hide() # Na wszelki wypadek
            results_page.setScreen(target_screen)
            geom = target_screen.geometry()
            results_page.move(geom.topLeft())
            
            results_page.show()
            results_page.showMaximized()
            results_page.raise_()
            results_page.activateWindow()
            print(f"on_test_complete: ResultsPage shown on screen 0, visibility={results_page.isVisible()}, geometry={results_page.geometry()}")
            
            # Opcjonalnie ukrywamy stack jeśli nadal żyje
            if controller.stack:
                controller.stack.hide()
                
            print("on_test_complete: ResultsPage shown as independent window on screen 0")

        controller.set_on_complete(on_test_complete)
        controller.start()

    controller.set_on_complete(on_tutorial_complete)

    # controller.start()

    def on_start_requested():
        meta = main_page.main_form.get_test_metadata()
        metrics.test_meta_data(TestMetaData(examine_id=meta.examine_id, patient_id=meta.patient_id))
        metrics.start_test()

        # Pobieramy listę wszystkich ekranów
        screens = QGuiApplication.screens()

        print(f"DEBUG: Wykryto {len(screens)} ekranów.")
        for idx, s in enumerate(screens):
            print(f"DEBUG: Ekran {idx}: {s.name()} | Geometry: {s.geometry()}")

        # Logika wyboru ekranu pacjenta:
        # Jeśli są co najmniej dwa ekrany, wybieramy drugi (indeks 1).
        # Jeśli jest tylko jeden, zostajemy na nim.
        target_screen = screens[1] if len(screens) > 1 else screens[0]
        print(f"DEBUG: Wybrany ekran docelowy: {target_screen.name()}")

        # Ukrywamy formularz lekarza
        main_page.close()

        # Ustawiamy ekran dla okna testowego przed startem
        # controller._stack to QStackedWidget, który jest głównym oknem testu
        stack = controller._stack
        
        # Wyłączamy tryb pełnoekranowy przed przeniesieniem, aby uniknąć problemów z geometrią
        stack.hide()
        
        # Przypisujemy do ekranu i przenosimy fizycznie na jego współrzędne
        stack.setScreen(target_screen)
        geom = target_screen.geometry()
        stack.move(geom.topLeft())
        
        print(f"DEBUG: Przenoszenie okna na: {geom.topLeft()}")

        controller.start()

    # Nasłuchiwanie kliknięcia "Rozpocznij" w formularzu głównym
    main_page.startRequested.connect(on_start_requested)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
