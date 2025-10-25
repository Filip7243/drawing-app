from collections.abc import Callable
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QWidget, QStackedWidget


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

    def set_sequence(self, factories: list[Callable[[], QWidget]]):
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

        if hasattr(page, "finished"):
            try:
                page.finished.connect(self._advance)
            except Exception:
                pass

        # Now safely remove and delete the previous page to avoid flicker
        if prev is not None:
            try:
                self._stack.removeWidget(prev)
            except Exception:
                pass
            prev.deleteLater()
