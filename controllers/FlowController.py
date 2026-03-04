from collections.abc import Callable

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QWidget, QStackedWidget

from controllers.TestMetrics import TestMetrics


class FlowController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._factories: list[Callable[[], QWidget]] = []
        self._idx = -1
        self._current: QWidget | None = None
        self._loop: bool = False
        self._on_complete: Callable[[], None] | None = None
        self._stack = QStackedWidget()
        self._metrics: TestMetrics | None = None
        self._test_mode: bool = False  # Sprawdza, czy jesteśmy w teście (w samouczku nie pobieramy danych)

    def set_metrics(self, metrics: TestMetrics | None):
        """
         Setter dla klasy metryk, która zbiera dane z rysowania i wylicza statystyki.
        """
        self._metrics = metrics

    def set_test_mode(self, enabled: bool):
        """
         Setter dla flagi test_mode, która włącza lub wyłącza tryb testowy. Tryb testowy determinuje czy
         dane są zbierane, czy to tylko samouczek.
        """
        self._test_mode = enabled

    def set_sequence(self, factories: list[Callable[[], QWidget]]):
        """
         Pozwala ustawić sekwencję widoków, które będą wyświetlane w trakcie testów. Tutaj ustawaimy listę
         z planszami i stronami do rysowania.
        """
        self._factories = factories
        self._idx = -1

    def set_loop(self, loop: bool):
        """
         Ustawia flagę loop, która pozwala wrócić na początek sekwencji samouczka, jeśli pacjent zechce
        """
        self._loop = loop

    def set_on_complete(self, callback: Callable[[], None] | None):
        """
         Ustawia callback, funkcja, która zostanie wywołana po zakończeniu całego testu, po to, aby zapisać dane.
        """
        self._on_complete = callback

    def start(self):
        """
         Funkcja do wystartowania testu.
        """
        if not self._stack.isVisible():
            if self._idx == -1:
                self._advance()
            
            # Jeśli okno ma przypisany konkretny ekran, upewnij się, że geometry jest z nim zgodne
            if self._stack.screen():
                geom = self._stack.screen().geometry()
                self._stack.move(geom.topLeft())
                
            self._stack.showMaximized()
        else:
            self._advance()

    def _restart_sequence(self):
        """
         Funkcja do restartu sekwencji samouczka.
        """
        self._idx = -1
        self._advance()

    def _advance(self):
        """
         Główna funkcja kontrolera, punkt centralny aplikacji.
         Przechwytuje wszystkie eventy wyemitowane podczas rysowania, umożliwia przejście do następnego widoku,
         zarządza stosem sekwencji samouczka i głównego testu.
        """
        prev = self._current

        self._idx += 1
        # Jeśli jesteśmy w ostatnim widoku sekwencji wywołujemy funkcję on_complete
        if self._idx >= len(self._factories):
            print(f"FlowController: sequence end reached. idx={self._idx}")
            if self._on_complete is not None:
                try:
                    print("FlowController: calling on_complete")
                    self._on_complete()
                finally:
                    # Nawet po on_complete usuwamy ostatni widget sekwencji
                    if prev is not None:
                        try:
                            print(f"FlowController: removing last sequence widget: {prev}")
                            self._stack.removeWidget(prev)
                            prev.deleteLater()
                        except Exception as e:
                            print(f'Błąd podczas usuwania ostatniego widoku: {e}')
                    return

            # Jeśli jesteśmy w trybie loop, restartujemy sekwencję
            if self._loop and len(self._factories) > 0:
                self._restart_sequence()
            return

        # Ustawienie aktualnej strony
        page = self._factories[self._idx]()
        page.setParent(self._stack)
        self._stack.addWidget(page)
        self._stack.setCurrentWidget(page)
        self._current = page

        # Podpięcie eventu dla audio, kliknięcie przycisku dalej
        if hasattr(page, "nextRequested"):
            try:
                page.nextRequested.connect(self._advance)
            except Exception as e:
                print(f"Coś poszło nie tak przy nextRequested: {e}")
                pass

        # Podpięcie eventu dla audio, kliknięcie przycisku powtórz,
        # jeśli jesteśmy, na ostatniej stronie to wracamy do początku sekwencji,
        # jeśli nie to odpalamy stronę, na której jesteśmy jeszcze raz.
        if hasattr(page, "repeatRequested"):
            try:
                is_last = (self._idx == len(self._factories) - 1)
                if is_last and self._loop:
                    page.repeatRequested.connect(self._restart_sequence)
                else:
                    start = getattr(page, "start", None)
                    if callable(start):
                        page.repeatRequested.connect(start)
            except Exception as e:
                print(f"Coś poszło nie tak przy repeatRequested: {e}")
                pass

        # Jeśli widok ma funkcję start, to wywołuje ją, taka funkcja służy do inicjalizacji widoku
        start = getattr(page, "start", None)
        if callable(start):
            start()

        # Jeśli jesteśmy w trybie testu to łapiemy wszystkie eventy emitowane w DrawingPage.py i podpinamy pod nie
        # odpowiednie funkcje z TestMetrics.py
        if self._test_mode and getattr(page, "is_drawing_page", False):
            if self._metrics is not None:
                self._metrics.start_drawing()
                if hasattr(page, "firstStroke"):
                    page.firstStroke.connect(self._metrics.record_first_stroke)
                if hasattr(page, "strokeStarted"):
                    page.strokeStarted.connect(self._metrics.record_stroke_start)
                if hasattr(page, "strokeFinished"):
                    page.strokeFinished.connect(self._metrics.record_stroke_finish)
                if hasattr(page, "strokeDataCollected"):
                    page.strokeDataCollected.connect(self._metrics.record_stroke_data)
                if hasattr(page, "undoClicked"):
                    page.undoClicked.connect(self._metrics.record_undo)
                if hasattr(page, "redoClicked"):
                    page.redoClicked.connect(self._metrics.record_redo)

        # Jeśli funkcja ma atrybut finished, to znaczy, że jest to widok rysowania albo zapamiętywania
        if hasattr(page, "finished"):
            try:
                if self._test_mode and getattr(page, "is_drawing_page", False) and self._metrics is not None:
                    # Handler dla eventu finished emitowanego w DrawingPage.py
                    def _on_finished_drawing(current_page=page):
                        try:
                            # Pobieramy exporter do zdjęcia i wywołujemy finish_drawing, która zapisuje rysunek,
                            # a także zapisuje metryki rysunku
                            exporter = getattr(current_page, "exporter", None)
                            if callable(exporter):
                                img = exporter()
                                self._metrics.finish_drawing(img)
                        except Exception as e:
                            print("COS POSZLO NIE TAK przy zapisie!")
                            print(f"Błąd: {e}")
                            pass
                        finally:
                            self._advance()

                    page.finished.connect(_on_finished_drawing)
                else:
                    from pages.RememberFigurePage import RememberFigurePage
                    # Zapisywanie danych o wielkości wyświetlanej planszy do zapamiętywania,
                    # może się przydać przy mapowaniu współrzędnych z eye-trackera
                    if isinstance(page, RememberFigurePage):
                        display_info = page.get_display_info()
                        bg_path = getattr(page, "bg_path", None)
                        self._metrics.save_display_info(display_info, bg_path)
                    page.finished.connect(self._advance)
            except Exception as e:
                print(f"Coś poszło nie tak na finished! {e}")
                pass

        # Bezpieczne usuwanie poprzedniego widoku po przejściu do kolejnego, tak żeby przejście było płynne.
        if prev is not None:
            try:
                print(f"FlowController: removing previous widget: {prev}")
                self._stack.removeWidget(prev)
                prev.deleteLater()
            except Exception as e:
                print(f'Błąd podczas usuwania poprzedniego widoku: {e}')
                pass

    @property
    def stack(self):
        return self._stack
