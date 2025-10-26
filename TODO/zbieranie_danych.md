### Cel
- Automatycznie zapisywać każdy rysunek z kroku `DrawingPage` w części testowej do pliku JPG.
- Mierzyć czas całego testu oraz czas rysowania każdego obrazu osobno.
- Robić to „w tle” po kliknięciu „Dalej” (bez dodatkowych klików użytkownika), tzn. zapis następuje tuż przed przejściem do następnego kroku.

Poniżej masz prosty, czysty i rozszerzalny sposób w duchu obecnego OOP (FlowController + strony), bez zacieśniania zależności między stronami.

---

### Architektura w skrócie
- Nowa klasa `TestMetrics` – trzyma katalog sesji testu, start/stop testu, start/stop rysunku, zapis plików JPG i generuje raport (np. JSON/CSV) na końcu.
- Minimalne doposażenie `DrawingPage`:
  - zachowanie referencji do komponentu rysującego (`self.april_tags`),
  - marker `is_drawing_page = True` (żeby kontroler mógł wykryć „krok rysowania”),
  - metoda `export_as_image()` zwracająca `QImage` (przechwytuje sam widok rysunku bez paska z przyciskiem).
- Mała integracja w `FlowController`:
  - `set_metrics(TestMetrics | None)` – zastrzyk serwisu pomiarów,
  - podczas tworzenia strony, jeśli to rysowanie → `metrics.start_drawing(...)`,
  - przy `finished` strony rysowania → pobranie obrazu (`export_as_image()`), `metrics.finish_drawing(...)`, dopiero potem `advance()`.
- W `main.py`:
  - Utwórz `TestMetrics`.
  - Po zakończeniu tutorialu (w `on_tutorial_complete`) – `metrics.start_test()` i ustaw `on_complete` dla testu na domknięcie pomiarów `metrics.end_test()`.

---

### 1) Nowa klasa TestMetrics (np. `controllers/TestMetrics.py`)
```python
# controllers/TestMetrics.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from time import perf_counter
from datetime import datetime
import json
from typing import Any
from PyQt6.QtGui import QImage


@dataclass
class DrawingRecord:
    index: int
    filename: str
    started_at: float  # perf_counter
    finished_at: float  # perf_counter

    @property
    def duration_s(self) -> float:
        return self.finished_at - self.started_at


class TestMetrics:
    def __init__(self, base_dir: Path | None = None):
        self._base_dir = Path(base_dir) if base_dir else Path.cwd() / "outputs"
        self._session_dir: Path | None = None
        self._test_start: float | None = None
        self._test_end: float | None = None
        self._current_drawing_start: float | None = None
        self._records: list[DrawingRecord] = []
        self._drawing_counter: int = 0

    @property
    def session_dir(self) -> Path:
        if self._session_dir is None:
            # Tworzymy leniwo – gdy wystartuje test
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._session_dir = self._base_dir / f"test_{ts}"
            self._session_dir.mkdir(parents=True, exist_ok=True)
        return self._session_dir

    def start_test(self):
        _ = self.session_dir  # zapewnia utworzenie katalogu
        self._test_start = perf_counter()
        self._records.clear()
        self._drawing_counter = 0

    def end_test(self) -> dict[str, Any]:
        self._test_end = perf_counter()
        summary = {
            "total_duration_s": (self._test_end - self._test_start) if (self._test_start is not None) else None,
            "drawings": [
                {
                    **asdict(r),
                    "duration_s": r.duration_s,
                } for r in self._records
            ]
        }
        # Zapisz JSON-em dla wygody, można też CSV
        (self.session_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary

    def start_drawing(self):
        self._current_drawing_start = perf_counter()
        self._drawing_counter += 1

    def finish_drawing(self, image: QImage) -> DrawingRecord:
        if self._current_drawing_start is None:
            # awaryjnie traktujemy jak 0-długościowy rysunek
            self._current_drawing_start = perf_counter()
        finished_at = perf_counter()
        index = self._drawing_counter
        # Nazwa pliku: numer + timestamp dla pewności
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        fname = f"drawing_{index:02d}_{ts}.jpg"
        fpath = self.session_dir / fname
        # Zapis JPG (jakość 90). Uwaga: QImage.save zwraca bool – można obsłużyć błędy.
        image.save(str(fpath), "JPG", quality=90)
        rec = DrawingRecord(
            index=index,
            filename=fname,
            started_at=self._current_drawing_start,
            finished_at=finished_at,
        )
        self._records.append(rec)
        # Zerowanie startu pojedynczego rysunku
        self._current_drawing_start = None
        return rec
```

- Katalog sesji testu: `outputs/test_YYYYmmdd_HHMMSS`.
- Każdy rysunek: `drawing_XX_YYYYmmdd_HHMMSS_mmmmmm.jpg`.
- Podsumowanie: `summary.json` z czasem całego testu oraz każdego rysunku.

---

### 2) Zmiany w DrawingPage (bez łamania FlowController)
- Zachowaj referencję do `AprilTagsComponent`,
- Dodaj marker i metodę eksportu obrazu samego obszaru rysowania.

```python
# pages/DrawingPage.py
from PyQt6.QtCore import QDir, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QImage

from components.AprilTagsComponent import AprilTagsComponent
from components.StyledButton import StyledButton


class DrawingPage(QWidget):
    finished = pyqtSignal()

    # Marker dla FlowController
    is_drawing_page = True

    def __init__(self, parent=None, audio="05_odwzoruj_rysunek.wav", is_tutorial=True):
        super().__init__(parent)
        self.setWindowTitle("Draw Figure Page")
        self.audio = audio
        self.is_tutorial = is_tutorial

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Zachowujemy referencję – będzie potrzebna do eksportu obrazu
        self.april_tags = AprilTagsComponent(num_tags=4, show_canvas=True)
        main_layout.addWidget(self.april_tags)

        button_container = QWidget()
        button_container.setStyleSheet("background-color: white;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)

        done_button = StyledButton("Dalej", color="#000000", font_color="#FFFFFF")
        done_button.setFixedWidth(500)
        done_button.clicked.connect(self.on_done_btn_click)
        button_layout.addStretch()
        button_layout.addWidget(done_button)
        button_layout.addStretch()

        button_container.setFixedHeight(done_button.sizeHint().height())
        main_layout.addWidget(button_container)
        self.setLayout(main_layout)

        self.player = None
        if self.audio is not None:
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            self.audio_output.setVolume(1.0)

            dir_assets = QDir("assets:/audio")
            audio_path = dir_assets.absoluteFilePath(self.audio)
            self.player.setSource(QUrl.fromLocalFile(audio_path))

            self.player.stop()
            self.player.play()

    def export_as_image(self) -> QImage:
        """Zwraca obraz QImage przedstawiający sam obszar rysowania.
        Jeżeli AprilTagsComponent ma wewnętrzną powierzchnię na rysunek, można tu ewentualnie zawęzić.
        Na start – snapshot całego komponentu.
        """
        pix = self.april_tags.grab()  # QPixmap
        return pix.toImage()

    def on_done_btn_click(self):
        # Nie zapisujemy tutaj – FlowController zrobi to, aby zachować separację ról.
        self.finished.emit()
```

- Dzięki `is_drawing_page = True` FlowController rozpozna, że to krok rysowania.
- `export_as_image()` pozwala kontrolerowi pobrać obraz tuż przed przejściem dalej.
- Zostawiamy zapis i pomiary poza stroną, aby strona była „głupym” krokiem UI.

Jeżeli chcesz wycinać tylko obszar płótna (bez ramek/znaczników), wystarczy w tej metodzie odnieść się do wewnętrznego widżetu płótna w `AprilTagsComponent` (np. `self.april_tags.canvas.grab()`) – to drobna zmiana zależna od implementacji komponentu.

---

### 3) Integracja w FlowController
- Dodaj opcjonalne metody: `set_metrics(TestMetrics | None)` oraz logikę przy stronach rysowania.

```python
# controllers/FlowController.py (fragmenty do dodania/zmiany)
from controllers.TestMetrics import TestMetrics  # import gdy utworzysz klasę

class FlowController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... reszta jak masz
        self._metrics: TestMetrics | None = None
        self._test_mode: bool = False  # flaga czy obecna sekwencja to test

    def set_metrics(self, metrics: TestMetrics | None):
        self._metrics = metrics

    def set_test_mode(self, enabled: bool):
        self._test_mode = enabled

    # w _advance() – po utworzeniu page:
        page = self._factories[self._idx]()
        # ... dodanie do stacka, setCurrentWidget itd.

        # Jeśli to krok rysowania w trybie testu – zacznij pomiar rysunku
        if self._test_mode and getattr(page, "is_drawing_page", False):
            if self._metrics is not None:
                self._metrics.start_drawing()

        # Zamiast bezpośrednio: page.finished.connect(self._advance)
        if hasattr(page, "finished"):
            try:
                if self._test_mode and getattr(page, "is_drawing_page", False) and self._metrics is not None:
                    def _on_finished_for_drawing(p=page):
                        # eksport obrazu i zapis + rejestracja czasu
                        try:
                            exporter = getattr(p, "export_as_image", None)
                            if callable(exporter):
                                img = exporter()
                                self._metrics.finish_drawing(img)
                        except Exception:
                            # Nie blokuj przepływu, nawet jeśli zapis się nie powiedzie
                            pass
                        finally:
                            self._advance()
                    page.finished.connect(_on_finished_for_drawing)
                else:
                    page.finished.connect(self._advance)
            except Exception:
                pass
```

- Dzięki temu zapis i pomiary dzieją się „w tle” dokładnie w momencie kliknięcia „Dalej” na `DrawingPage` (przed przejściem do kolejnego kroku), a reszta kroków działa jak wcześniej.

---

### 4) Spięcie w main.py
- Tworzymy `TestMetrics`, włączamy tryb testu przy `TEST_SEQUENCE` i ustawiamy koniec testu na zapis podsumowania.

```python
# main.py (fragmenty)
from controllers.TestMetrics import TestMetrics

metrics = TestMetrics()  # domyślnie zapisze do .\outputs\test_...

controller = FlowController()
controller.set_sequence(TUTORIAL_SEQUENCE)
controller.set_loop(True)
controller.set_metrics(metrics)


def on_tutorial_complete():
    # Uruchamiamy TEST
    controller.set_loop(False)
    controller.set_on_complete(None)
    controller.set_sequence(TEST_SEQUENCE)
    controller.set_test_mode(True)
    metrics.start_test()

    def on_test_complete():
        summary = metrics.end_test()
        # Możesz tu np. wypisać do konsoli/logu, pokazać stronę "dziękujemy", itp.
        # print(summary)
        controller.set_test_mode(False)
        controller.set_on_complete(None)

    controller.set_on_complete(on_test_complete)
    controller.start()

controller.set_on_complete(on_tutorial_complete)
controller.start()
```

- `set_test_mode(True)` mówi kontrolerowi, że kroki rysowania w tej sekwencji trzeba mierzyć i zapisywać.
- `metrics.start_test()` inicjuje katalog sesji i licznik czasu testu.
- `on_test_complete` kończy test, zapisuje `summary.json` i czyści flagi.

---

### 5) Czy zapis JPG „zablokuje” UI?
- Zwykle snapshot widżetu i zapis JPG 90 jakości przy rozsądnych rozdzielczościach trwa ułamki sekundy i nie powinien powodować zauważalnego „przycięcia”.
- Jeśli natrafisz na opóźnienia (np. bardzo wysokie rozdzielczości), można bardzo łatwo offloadować sam zapis pliku do wątku roboczego (QThreadPool/QRunnable) – logika pozostaje taka sama; FlowController bierze obraz (`QImage`), a zapis robi worker w tle. Daj znać, przygotuję prosty `SaveImageTask`.

---

### 6) Opcjonalne rozszerzenia
- Znacznik czasu „start rysowania” dokładnie przy pierwszym ruchu piórkiem/myszą:
  - jeśli `AprilTagsComponent` wystawia sygnał np. `drawingStarted`, podepnij `metrics.start_drawing()` właśnie tam – wtedy pomiar będzie najdokładniejszy. W przeciwnym razie obecne „start przy wejściu na stronę” jest wystarczające i spójne.
- CSV obok JSON:
  - łatwo dopisać zapis do `summary.csv` iterując po `self._records`.
- Numer rysunku X w nazwie i w JSON masz w `index` – to rośnie automatycznie.
- Jeżeli chcesz zapisywać także podgląd całej strony (np. z przyciskiem) – możesz dodać drugą metodę `export_full_page()` i zapisywać oba.

---

### 7) Najmniejsza możliwa zmiana (jeśli chcesz bez ruszania FlowController)
- Alternatywa: cały zapis zrobić w `DrawingPage.on_done_btn_click()` – wywołać `self.export_as_image()`, zapisać do katalogu sesji i dopiero `self.finished.emit()`. Wtedy jednak `DrawingPage` musi wiedzieć o katalogu sesji i liczniku rysunków (czyli wstrzyknąć mu `metrics`). To ciaśniej wiąże stronę z infrastrukturą – dlatego rekomenduję wariant z FlowController.

---

### Podsumowanie
- Dodajesz jedną klasę `TestMetrics`, dwa małe haki w `FlowController`, drobny marker + metoda eksportu w `DrawingPage`, i 3 linijki w `main.py`.
- Efekt: po naciśnięciu „Dalej” w każdym kroku rysowania w teście obraz zapisywany jest jako JPG w katalogu sesji, liczony jest czas rysowania pojedynczego obrazu oraz całej sekwencji testowej, a na końcu powstaje `summary.json` z kompletem danych do dalszej analizy.