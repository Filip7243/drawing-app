from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from time import perf_counter
from typing import Any, Optional

from PyQt6.QtCore import QBuffer, QIODeviceBase
from PyQt6.QtGui import QImage

from db.models import TestMetaData, Image
from db.repository.ImageRepository import ImageRepository
from db.service.ExaminationService import ExaminationService


@dataclass
class DrawingRecord:
    """
    Klasa reprezentująca dane pojedynczego rysunku w teście BVRT.

    Attributes:
        index (int): Identyfikator rysunku.
        filename (str): Nazwa pliku z rysunkiem (np. `id_pacjenta-id_badania-index.png`).
        started_at (float): Czas (timestamp) pojawienia się planszy do rysowania.
        finished_at (float): Czas (timestamp) kliknięcia przycisku "Dalej", gdy badany uznał, że zakończył rysunek.
    """
    index: int
    filename: str
    patient_id: int
    examine_id: int
    started_at: float
    finished_at: float
    display_info: Optional[dict] = field(default=None)

    @property
    def duration_s(self) -> float:
        """
        Oblicza czas trwania rysowania w sekundach..

        Returns:
            float: Różnica między `finished_at` a `started_at` w sekundach.
        """
        return self.finished_at - self.started_at


def image_to_bytes(image):
    buffer = QBuffer()
    buffer.open(QIODeviceBase.OpenModeFlag.ReadWrite)
    try:
        image.save(buffer, "PNG")
        return bytes(buffer.data())
    finally:
        buffer.close()


class TestMetrics:
    imageRepository = ImageRepository()
    examinationService = ExaminationService()

    def __init__(self, base_dir: Path | None = None):
        """Serwis do zbierania i zapisywania danych z badania BVRT.

        Klasa umożliwia:
        - Pomiar czasu trwania całego testu
        - Rejestrację czasów rysowania poszczególnych obrazków
        - Zapis rysunków do plików PNG
        - Eksport danych do pliku JSON

        Attributes:
            session_dir: Ścieżka do katalogu z danymi bieżącej sesji testowej.
        """
        self._base_dir = Path(base_dir) if base_dir else Path.home() / "bvrt" / "outputs"
        print(f"base dir: {self._base_dir}")
        self._test_meta_data: TestMetaData | None = None
        self._session_dir: Path | None = None
        self._test_start: float | None = None
        self._test_end: float | None = None
        self._current_drawing_start: float | None = None
        self._records: list[DrawingRecord] = []
        self._drawing_counter: int = 0
        self._current_display_info: dict | None = None

    @property
    def session_dir(self) -> Path:
        if self._session_dir is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._session_dir = (
                    self._base_dir / f"test_{ts}_{self._test_meta_data.patient_id}_{self._test_meta_data.examine_id}"
            )
            self._session_dir.mkdir(parents=True, exist_ok=True)
        return self._session_dir

    def test_meta_data(self, test_meta_data: TestMetaData):
        self._test_meta_data = test_meta_data

    def start_test(self):
        _ = self.session_dir  # Tworzy katalog sesji, jeśli nie istnieje
        self._test_start = perf_counter()
        self._records.clear()  # Usuwamy poprzednie rekordy (jeśli istnieją)
        self._drawing_counter = 0
        self._current_display_info = None

    def end_test(self) -> dict[str, Any]:
        """
        Kończy test BVRT i zapisuje jego dane do pliku JSON.
        Dane zapisane w pliku `summary.json` mają następującą strukturę:

        ```json
        {
            "total_duration": 123.45,
            "drawings": [
                {
                    "index": 0,
                    "filename": "id_pacjenta-id_badania-0.png",
                    "started_at": 123.45,
                    "finished_at": 246.90,
                    "duration_s": 123.45
                }
            ]
        }
        ```

        :returns:
            dict[str, Any]: Słownik zawierający podsumowanie testu, w tym całkowity czas trwania (`total_duration`)
            oraz listę rysunków (`drawings`) z czasami rysowania.
        """
        self._test_end = perf_counter()
        summary = {
            "total_duration": (self._test_end - self._test_start) if (self._test_end and self._test_start) else None,
            "drawings": [
                {
                    **asdict(record),  # zmieniamy każdy rekord (rysunek) na słownik
                    "duration_s": record.duration_s,  # dodajemy czas trwania rysowania w sekundach
                } for record in self._records
            ]
        }
        self.examinationService.update_examination_times(self._test_meta_data.examine_id,
                                                         whole_time=timedelta(seconds=summary["total_duration"]),
                                                         avg_time=timedelta(
                                                             seconds=summary["total_duration"] / len(self._records)))
        # zapisujemy do JSON
        (self.session_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary

    def save_display_info(self, display_info: dict | None):
        """
        NOWE: Zapisuje informacje o wyświetlaniu wzorca.
        Wywoływane po zakończeniu RememberFigurePage.

        :param display_info: Słownik z parametrami wyświetlania z RememberFigurePage.get_display_info()
        """
        self._current_display_info = display_info
        if display_info:
            print(f"📋 Zapisano display_info dla rysunku {self._drawing_counter + 1}: "
                  f"{display_info['window_width']}x{display_info['window_height']}")

    def start_drawing(self):
        self._current_drawing_start = perf_counter()
        self._drawing_counter += 1

    def finish_drawing(self, image: QImage) -> DrawingRecord:
        """
        Kończy rysowanie i zapisuje wszystkie dane wraz z rysunkiem w formacie PNG.
        :param image: Rysunek do zapisu
        :return: Dane szczegółowe o każdym z rysunków
        """
        if self._current_drawing_start is None:
            self._current_drawing_start = perf_counter()

        finished_at = perf_counter()
        index = self._drawing_counter
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{index}_{ts}_{self._test_meta_data.patient_id}_{self._test_meta_data.examine_id}.png"
        filepath = self.session_dir / filename
        image.save(str(filepath), "PNG", quality=100)
        new_record = DrawingRecord(
            index,
            filename,
            self._test_meta_data.patient_id,
            self._test_meta_data.examine_id,
            self._current_drawing_start,
            finished_at,
            display_info=self._current_display_info  # NOWE: dołączamy zapisane info
        )
        self._records.append(new_record)
        image_record = Image(self._test_meta_data.examine_id, image_to_bytes(image),
                             timedelta(seconds=new_record.duration_s))
        self.imageRepository.insert_image(image_record)
        self._current_drawing_start = None
        self._current_display_info = None  # NOWE: czyścimy po użyciu

        return new_record
