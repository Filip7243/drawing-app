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
        # Persistent container to avoid desktop flicker between steps
        self._stack = QStackedWidget()
        self._metrics: TestMetrics | None = None
        self._test_mode: bool = False  # Sprawdza, czy jesteśmy w teście (w samouczku nie pobieramy danych)

    def set_metrics(self, metrics: TestMetrics | None):
        self._metrics = metrics

    def set_test_mode(self, enabled: bool):
        self._test_mode = enabled

    def set_sequence(self, factories: list[Callable[[], QWidget]]):
        print(f"USTAWIWAM FACTORIES: {factories}")
        self._factories = factories
        self._idx = -1

    def set_loop(self, loop: bool):
        self._loop = loop

    def set_on_complete(self, callback: Callable[[], None] | None):
        self._on_complete = callback

    def start(self):
        # Ensure the very first page is created BEFORE showing the window,
        # so the stack maximizes with correct initial content size
        if not self._stack.isVisible():
            if self._idx == -1:
                self._advance()  # prepares the first page in the stack
            self._stack.showMaximized()
        else:
            # When the stack is already visible (e.g., switching sequences), just advance
            self._advance()

    def _restart_sequence(self):
        self._idx = -1
        self._advance()

    def _advance(self):
        prev = self._current

        self._idx += 1
        if self._idx >= len(self._factories):
            # Do not tear down the current widget yet; let on_complete or loop decide next
            if self._on_complete is not None:
                try:
                    self._on_complete()
                finally:
                    return
            if self._loop and len(self._factories) > 0:
                self._restart_sequence()
            return

        # Create next page and insert into the persistent stack
        page = self._factories[self._idx]()
        page.setParent(self._stack)
        self._stack.addWidget(page)
        self._stack.setCurrentWidget(page)
        self._current = page

        # Wire signals for navigation
        if hasattr(page, "nextRequested"):
            try:
                page.nextRequested.connect(self._advance)
            except Exception:
                pass

        if hasattr(page, "repeatRequested"):
            try:
                is_last = (self._idx == len(self._factories) - 1)
                if is_last and self._loop:
                    page.repeatRequested.connect(self._restart_sequence)
                else:
                    start = getattr(page, "start", None)
                    if callable(start):
                        page.repeatRequested.connect(start)
            except Exception:
                pass

        # Start or show the page (avoid showMaximized when embedded)
        start = getattr(page, "start", None)
        if callable(start):
            start()

        if self._test_mode and getattr(page, "is_drawing_page", False):
            if self._metrics is not None:
                self._metrics.start_drawing()
                if hasattr(page, "firstStroke"):
                    page.firstStroke.connect(self._metrics.record_first_stroke)
                if hasattr(page, "strokeStarted"):
                    page.strokeStarted.connect(self._metrics.record_stroke_start)
                if hasattr(page, "strokeFinished"):
                    page.strokeFinished.connect(self._metrics.record_stroke_finish)
                if hasattr(page, "undoClicked"):
                    page.undoClicked.connect(self._metrics.record_undo)
                if hasattr(page, "redoClicked"):
                    page.redoClicked.connect(self._metrics.record_redo)

        if hasattr(page, "finished"):
            try:
                if self._test_mode and getattr(page, "is_drawing_page", False) and self._metrics is not None:
                    def _on_finished_drawing(current_page=page):
                        try:
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
                    if isinstance(page, RememberFigurePage):
                        display_info = page.get_display_info()
                        self._metrics.save_display_info(display_info)
                    page.finished.connect(self._advance)
            except Exception:
                print("Coś poszło nie tak na finished!")
                pass

        # Now safely remove and delete the previous page to avoid flicker
        if prev is not None:
            try:
                self._stack.removeWidget(prev)
            except Exception:
                pass
            prev.deleteLater()

    @property
    def stack(self):
        return self._stack
