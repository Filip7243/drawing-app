from __future__ import annotations

import json
import time
import traceback
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from time import perf_counter
from typing import Any, Optional

from PyQt6.QtCore import QBuffer, QIODeviceBase, Qt
from PyQt6.QtGui import QImage, QPainter, QColor, QPen, QPixmap

from db.models import TestMetaData, Image
from db.repository.ImageRepository import ImageRepository
from db.service.ExaminationService import ExaminationService

SCRUBBING_THRESHOLD = 100


@dataclass
class DrawingRecord:
    """
    Klasa reprezentująca dane pojedynczego rysunku w teście BVRT.

    Attributes:
        index (int): Identyfikator rysunku.
        filename (str): Nazwa pliku z rysunkiem (np. `id_pacjenta-id_badania-index.png`).
        started_at (float): Czas pojawienia się planszy do rysowania.
        started_at_ts (float): Czas (timestamp) pojawienia się planszy do rysowania.
        first_stroke_at (float): Czas pierwszego dotknięcia płótna.
        first_stroke_at_ts (float): Czas (timestamp) pierwszego dotknięcia płótna.
        finished_at (float): Czas kliknięcia przycisku "Dalej", gdy badany uznał, że zakończył rysunek.
        finished_at_ts (float): Czas (timestamp) kliknięcia przycisku "Dalej", gdy badany uznał, że zakończył rysunek.
        interruptions_count (int): Ilość oderwań rysika od płótna.
        interruption_durations (list[float]): Lista czasów trwania poszczególnych przerw (w sekundach).
        overdrawing_score (float): Stosunek pikseli nadrysowanych do wszystkich narysowanych pikseli.
        revisits_count (int): Liczba unikalnych powrotów do wcześniej odwiedzonych sekcji płótna.
        shading_detected (bool): Czy wykryto próby zamazywania/cieniowania.
        direction_changes_count (int): Liczba znaczących zmian kierunku podczas rysowania.
        display_info: Optional[dict]: Informacje o plnaszy do zapamiętania (szerokość, wysokość, etc.)
        overlay_filename: nazwa pliku z nałożonym rysunkiem badanego na oryginał
        heatmap_filename:  nazwa pliku heatmapy
        strokes_data: współrzędne każdego namalowanego piksela wraz z timestamp
    """
    index: int
    filename: str
    patient_id: int
    examine_id: int
    started_at: float
    started_at_ts: float
    first_stroke_at: Optional[float]
    first_stroke_at_ts: Optional[float]
    finished_at: float
    finished_at_ts: float
    interruptions_count: int = 0
    interruption_durations: list[float] = field(default_factory=list)
    undo_count: int = 0
    redo_count: int = 0
    overdrawing_score: float = 0.0
    revisits_count: int = 0
    shading_detected: bool = False
    direction_changes_count: int = 0
    rapid_velocity_changes_count: int = 0
    avg_velocity: float = 0.0
    max_velocity: float = 0.0
    velocity_ratio: float = 0.0
    velocity_profile_filename: Optional[str] = None
    display_info: Optional[dict] = field(default=None)
    overlay_filename: Optional[str] = None
    heatmap_filename: Optional[str] = None
    strokes_data: list[list[tuple[float, int, int]]] = field(default_factory=list)

    @property
    def duration_s(self) -> float:
        """
        Oblicza czas trwania od pojawienia się planszy do zakończenia w sekundach (kliknięcia "Dalej" przez pacjenta).

        Returns:
            float: Różnica między `finished_at` a `started_at` in sekundach.
        """
        return self.finished_at - self.started_at

    @property
    def actual_drawing_duration_s(self) -> Optional[float]:
        """
        Oblicza czas właściwego rysowania w sekundach (od pierwszego dotknięcia do zakończenia).

        Returns:
            Optional[float]: Różnica między `finished_at` a `first_stroke_at` w sekundach lub None,
             jeśli nie oddano żadnego śladu.
        """
        if self.first_stroke_at is None:
            return None
        return self.finished_at - self.first_stroke_at

    @property
    def avg_interruption_duration_s(self) -> Optional[float]:
        """
        Oblicza średni czas trwania przerwy w rysowaniu.

        Returns:
            Optional[float]: Średni czas w sekundach lub None, jeśli nie było przerw.
        """
        if not self.interruption_durations:
            return None
        return sum(self.interruption_durations) / len(self.interruption_durations)


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

        Attributes:
            _session_dir: Ścieżka do katalogu z danymi bieżącej sesji testowej.
        """
        self._base_dir = Path(base_dir) if base_dir else Path.home() / "bvrt" / "outputs"
        print(f"base dir: {self._base_dir}")
        self._test_meta_data: TestMetaData | None = None
        self._session_dir: Path | None = None
        self._test_start: float | None = None
        self._test_start_unix: float | None = None
        self._test_end: float | None = None
        self._current_drawing_start: float | None = None
        self._current_drawing_start_ts: float | None = None
        self._current_first_stroke: float | None = None
        self._current_first_stroke_ts: float | None = None
        self._current_interruptions_count: int = 0
        self._current_interruption_durations: list[float] = []
        self._current_undo_count: int = 0
        self._current_redo_count: int = 0
        self._current_overdrawing_pixels: int = 0
        self._current_total_drawn_pixels: int = 0
        self._current_revisits_count: int = 0
        self._current_shading_detected: bool = False
        self._current_direction_changes_count: int = 0
        self._current_rapid_velocity_changes_count: int = 0
        self._current_velocities: list[float] = []
        self._current_strokes: list[list[tuple[float, int, int]]] = []
        self._visited_grid_cells: set[tuple[int, int]] = set()
        self._grid_visit_counts: dict[tuple[int, int], int] = {}
        self._grid_overdraw_counts: dict[tuple[int, int], int] = {}
        self._grid_size: int = 40  # rozmiar komórki siatki w pikselach
        self._last_stroke_finish_at: float | None = None
        self._records: list[DrawingRecord] = []
        self._drawing_counter: int = 0
        self._current_display_info: dict | None = None
        self._current_reference_path: str | None = None

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
        self._test_start_unix = time.time()
        self._records.clear()  # Usuwamy poprzednie rekordy (jeśli istnieją)
        self._drawing_counter = 0
        self._current_display_info = None

    def end_test(self) -> dict[str, Any]:
        """
        Kończy test BVRT i zapisuje jego dane do pliku JSON.
        Dane zapisane w pliku `summary.json` mają następującą strukturę:

        :returns:
            Dict [str., Any]: Słownik zawierający podsumowanie testu, w tym całkowity czas trwania (`total_duration_s`)
            oraz listę rysunków (`drawings`) z czasami rysowania.
        """
        try:
            self._test_end = perf_counter()
            self._test_end_ts = time.time()
            total_duration_s = (self._test_end - self._test_start) if (self._test_end and self._test_start) else 0.0
            summary = {
                "test_start_unix": self._test_start_unix,
                "test_start_perf": self._test_start,
                "total_duration_s": total_duration_s,
                "test_end_ts": self._test_end_ts,
                "drawings": [
                    {
                        **asdict(record),  # zmieniamy każdy rekord (rysunek) na słownik
                        "duration_s": record.duration_s,
                        "actual_drawing_duration_s": record.actual_drawing_duration_s,
                        "avg_interruption_duration_s": record.avg_interruption_duration_s,
                    } for record in self._records
                ]
            }
            num_records = len(self._records)
            avg_time_s = (total_duration_s / num_records) if num_records > 0 else 0.0

            self.examinationService.update_examination_times(self._test_meta_data.examine_id,
                                                             whole_time=timedelta(seconds=total_duration_s),
                                                             avg_time=timedelta(seconds=avg_time_s))
            # zapisujemy do JSON
            (self.session_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
            return summary
        except Exception as e:
            print(f"Error in end_test: {e}")
            traceback.print_exc()
            raise e

    def save_display_info(self, display_info: dict | None, reference_path: str | None = None):
        """
        Zapisuje informacje o wyświetlaniu wzorca oraz ścieżkę do niego. Wywoływane po zakończeniu RememberFigurePage.

        :param display_info: Słownik z parametrami wyświetlania z RememberFigurePage.get_display_info()
        :param reference_path: Ścieżka do pliku graficznego wzorca.
        """
        self._current_display_info = display_info
        self._current_reference_path = reference_path
        if display_info:
            print(f"Zapisano display_info i path ({reference_path}) dla rysunku {self._drawing_counter + 1}")

    def start_drawing(self):
        self._current_drawing_start = perf_counter()
        self._current_drawing_start_ts = time.time()
        self._current_first_stroke = None
        self._current_first_stroke_ts = None
        self._current_interruptions_count = 0
        self._current_interruption_durations = []
        self._current_undo_count = 0
        self._current_redo_count = 0
        self._current_overdrawing_pixels = 0
        self._current_total_drawn_pixels = 0
        self._current_revisits_count = 0
        self._current_shading_detected = False
        self._current_direction_changes_count = 0
        self._current_rapid_velocity_changes_count = 0
        self._current_velocities = []
        self._current_strokes = []
        self._visited_grid_cells = set()
        self._grid_visit_counts = {}
        self._grid_overdraw_counts = {}
        self._last_stroke_finish_at = None
        self._drawing_counter += 1

    def record_first_stroke(self):
        """
            Zapisuje czas pierwszego dotknięcia płótna. Handler dla eventu firstStroke emitowanego w DrawingCanvas.py
        """
        if self._current_first_stroke is None:
            self._current_first_stroke = perf_counter()
            self._current_first_stroke_ts = time.time()
            print(f"Pierwsze dotknięcie płótna: {self._current_first_stroke}")

    def record_stroke_start(self):
        """
         Obliczamy czas trwania przerwy pomiędzy rysowanymi liniami oraz zliczamy ich ogólną ilość,
         to pozwala nam stwierdzić, jak długo dziecko myśli między rysowaniem kolejnych części rysunku.
         Handler dla eventu strokeStarted emitowanego w DrawingCanvas.py
        """
        if self._last_stroke_finish_at is not None:
            duration = perf_counter() - self._last_stroke_finish_at
            self._current_interruption_durations.append(duration)
            self._current_interruptions_count += 1
            print(f"Przerwa trwała: {duration:.4f}s (łącznie przerw: {self._current_interruptions_count})")
        self._last_stroke_finish_at = None

    def record_stroke_finish(self):
        """
         Timestamp zakończenia rysowania pojedynczej linii.
         Potrzebne do obliczania czasu trwania przerwy pomiędzy rysowanymi liniami.
         Handler dla eventu strokeFinished emitowanego w DrawingCanvas.py
        """
        self._last_stroke_finish_at = perf_counter()

    def record_undo(self):
        """
         Zlicza ilość kliknięć przycisku UNDO.
         Handler dla eventu undoClicked emitowanego w DrawingCanvas.py
        """
        self._current_undo_count += 1
        print(f"Kliknięto UNDO. Licznik: {self._current_undo_count}")

    def record_redo(self):
        """
         Zlicza ilość kliknięć przycisku REDO.
         Handler dla eventu redoClicked emitowanego w DrawingCanvas.py
        """
        self._current_redo_count += 1
        print(f"Kliknięto REDO. Licznik: {self._current_redo_count}")

    def record_stroke_data(self, stroke_data: dict):
        """
        Rejestruje dane o zakończonej kresce. Dane przychodzą z DrawingCanvas.py,
        metoda jest uruchomiana na event emit event strokeDataCollected.
        stroke_data = {
            'overdrawn_pixels': ilość pikseli nadpisanych ("malowanie w miejscu")
            'total_pixels': ilość narysowanych linii globalnie dla całego rysunku
                (linia = narysowane piksele od momentu kliknięcia myszki/przyłożenia,
                rysiku do ekranu, aż do momentu puszczenia),
            'points': współrzędne wszystkich punktów narysowanej linii, wraz z timestamp narysowania każdego z punktów,
            'path_length': długość ścieżki całego narysowanego rysunku,
                może się również przydać do porównania długości oryginalnego rysunku z rysunkiem badanego,
            'bounding_box_area': Pole powierzchni narysowanej linii. Porównujemy ją z wyliczoną drogą (path_length),
                w celu sprawdzenia, czy nastąpiło "rysowanie w miejscu"
            'direction_changes': ilość zmian kierunku rysowania,
            'overdraw_cells': komórki (siatka 40x40), w których rysowano kilka razy różne linie.
                Czyli powrócono do danej sekcji obrazu. Trzeba dobrze przetestować,
                bo czasami rysunki nachodzą na siebie, i to wcale nie musi oznaczać błędu.
        }
        Handler dla eventu strokeDataCollected emitowanego w DrawingCanvas.py
        """
        self._current_overdrawing_pixels += stroke_data.get('overdrawn_pixels', 0)
        self._current_total_drawn_pixels += stroke_data.get('total_pixels', 0)
        self._current_direction_changes_count += stroke_data.get('direction_changes', 0)
        self._current_rapid_velocity_changes_count += stroke_data.get('rapid_velocity_changes', 0)
        self._current_velocities.extend(stroke_data.get('velocity_profile', []))

        # Zapisujemy surowe dane punktów narysowanej linii wraz z ich timestampami.
        points = stroke_data.get('points', [])
        self._current_strokes.append(points)

        path_length = stroke_data.get('path_length', 0)
        bbox_area = stroke_data.get('bounding_box_area', 1)
        # Obliczamy stosunek długości narysowanej linii do obszaru, jaki zajmuje,
        # jeśli droga bardzo długa, a obszar mały to znaczy, że jest cieniowanie/szorowanie ("malowanie w miejscu")
        # SCRUBBING_THRESHOLD do dostosowania
        if bbox_area > 0 and (path_length * path_length) / bbox_area > SCRUBBING_THRESHOLD:
            print(f'path_len:{path_length}')
            print(f'bbox_area:{bbox_area}')
            print(f'SCRUBBING_THRESHOLD:{SCRUBBING_THRESHOLD}')
            area = (path_length * path_length) / bbox_area
            print(f'(path_length * path_length) / bbox_area:{area}')
            self._current_shading_detected = True
            print("Wykryto cieniowanie/szorowanie!")

        # Detekcja ponownego odwiedzania obszarów
        stroke_visited_cells = set()
        for ts, t, x, y, _, _ in points:
            cell = (x // self._grid_size, y // self._grid_size)
            stroke_visited_cells.add(cell)

        # Sprawdzamy, czy ta kreska wchodzi w komórki odwiedzone przez POPRZEDNIE kreski
        revisit_detected_in_this_stroke = False
        for cell in stroke_visited_cells:
            # Heatmap: zwiększamy licznik dla każdej odwiedzonej komórki w tej kresce
            self._grid_visit_counts[cell] = self._grid_visit_counts.get(cell, 0) + 1

            if cell in self._visited_grid_cells:
                revisit_detected_in_this_stroke = True

        # Zliczamy, ile było re-wizyt ogólnie
        if revisit_detected_in_this_stroke:
            self._current_revisits_count += 1
            print(f"Powrót do wcześniej odwiedzonego obszaru (łącznie powrotów: {self._current_revisits_count})")

        # Aktualizujemy globalną siatkę odwiedzin dla tego rysunku
        self._visited_grid_cells.update(stroke_visited_cells)

        # Potrzebne przy generowaniu heatmap
        overdraw_cells = stroke_data.get('overdraw_cells', {})
        for cell, count in overdraw_cells.items():
            self._grid_overdraw_counts[cell] = self._grid_overdraw_counts.get(cell, 0) + count

    def finish_drawing(self, image: QImage) -> DrawingRecord:
        """
        Kończy rysowanie i zapisuje wszystkie dane wraz z rysunkami
         w formacie PNG (rysunek, obrazy nakładki (overlay) i heatmapy).
        """
        if self._current_drawing_start is None:
            self._current_drawing_start = perf_counter()
            self._current_drawing_start_ts = time.time()

        finished_at = perf_counter()
        finished_at_ts = time.time()
        index = self._drawing_counter
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        base_filename = f"{index}_{ts}_{self._test_meta_data.patient_id}_{self._test_meta_data.examine_id}"
        filename = f"{base_filename}.png"
        filepath = self.session_dir / filename
        image.save(str(filepath), "PNG", quality=100)

        # 1. Generowanie i zapisywanie Overlay
        overlay_img = self._generate_overlay(image)
        overlay_filename = None
        if overlay_img:
            overlay_filename = f"{base_filename}_overlay.png"
            overlay_path = self.session_dir / overlay_filename
            overlay_img.save(str(overlay_path), "PNG")

        # 2. Generowanie i zapisywanie Heatmapy
        heatmap_img = self._generate_heatmap(image)
        heatmap_filename = None
        if heatmap_img:
            heatmap_filename = f"{base_filename}_heatmap.png"
            heatmap_path = self.session_dir / heatmap_filename
            heatmap_img.save(str(heatmap_path), "PNG")

        # 3. Generowanie i zapisywanie profilu prędkości (krzywa log-normalna)
        velocity_profile_filename = None
        if self._current_velocities:
            velocity_img = self._generate_velocity_profile_image()
            if velocity_img:
                velocity_profile_filename = f"{base_filename}_velocity.png"
                velocity_path = self.session_dir / velocity_profile_filename
                velocity_img.save(str(velocity_path), "PNG")

        avg_vel = sum(self._current_velocities) / len(self._current_velocities) if self._current_velocities else 0.0
        max_vel = max(self._current_velocities) if self._current_velocities else 0.0
        vel_ratio = avg_vel / max_vel if max_vel > 0 else 0.0

        overdrawing_score = 0.0
        # Wylicza score "rysowania w miejscu", im większy, tym częściej się to powtarzało na rysunku
        # Score to stosunek liczby pikseli "rysowanych w miejscu" do wszystkich rysowanych pikseli
        if self._current_total_drawn_pixels > 0:
            overdrawing_score = self._current_overdrawing_pixels / self._current_total_drawn_pixels

        # Znaczenie każdej ze składowych new_record opisałem powyżej w dataclass DrawingRecord
        new_record = DrawingRecord(
            index,
            filename,
            self._test_meta_data.patient_id,
            self._test_meta_data.examine_id,
            self._current_drawing_start,
            self._current_drawing_start_ts,
            self._current_first_stroke,
            self._current_first_stroke_ts,
            finished_at,
            finished_at_ts,
            interruptions_count=self._current_interruptions_count,
            interruption_durations=list(self._current_interruption_durations),
            undo_count=self._current_undo_count,
            redo_count=self._current_redo_count,
            overdrawing_score=overdrawing_score,
            revisits_count=self._current_revisits_count,
            shading_detected=self._current_shading_detected,
            direction_changes_count=self._current_direction_changes_count,
            rapid_velocity_changes_count=self._current_rapid_velocity_changes_count,
            avg_velocity=avg_vel,
            max_velocity=max_vel,
            velocity_ratio=vel_ratio,
            velocity_profile_filename=velocity_profile_filename,
            display_info=self._current_display_info,
            overlay_filename=overlay_filename,
            heatmap_filename=heatmap_filename,
            strokes_data=list(self._current_strokes)
        )
        # Zapis danych konkretnego rysunku do listy wszystkich, na koniec w funkcji end_test lista zostanie sparsowana
        # do json i zapisana w pliku summary.json w katalogu testu
        self._records.append(new_record)
        image_record = Image(self._test_meta_data.examine_id, image_to_bytes(image),
                             timedelta(seconds=new_record.duration_s))
        self.imageRepository.insert_image(image_record)

        # Czyszczenie stanu po zakończeniu rysowania
        self._current_drawing_start = None
        self._current_drawing_start_ts = None
        self._current_first_stroke = None
        self._current_first_stroke_ts = None
        self._current_interruptions_count = 0
        self._current_interruption_durations = []
        self._current_undo_count = 0
        self._current_redo_count = 0
        self._current_overdrawing_pixels = 0
        self._current_total_drawn_pixels = 0
        self._current_revisits_count = 0
        self._current_shading_detected = False
        self._current_direction_changes_count = 0
        self._current_rapid_velocity_changes_count = 0
        self._current_velocities = []
        self._current_strokes = []
        self._visited_grid_cells = set()
        self._grid_visit_counts = {}
        self._grid_overdraw_counts = {}
        self._last_stroke_finish_at = None
        self._current_display_info = None
        self._current_reference_path = None

        return new_record

    def _generate_overlay(self, user_image: QImage) -> Optional[QImage]:
        """Generuje obraz nałożenia rysunku dziecka na wzorzec."""
        if not self._current_display_info or not self._current_reference_path:
            return None

        display_info = self._current_display_info
        # Używamy ścieżki bezpośrednio (Qt obsłuży assets: dzięki addSearchPath)
        background_pixmap = QPixmap(self._current_reference_path)

        if background_pixmap.isNull():
            print(f"Nie udało się wczytać wzorca do overlay: {self._current_reference_path}")
            return None

        canvas_width = user_image.width()
        canvas_height = user_image.height()

        combined = QImage(canvas_width, canvas_height, QImage.Format.Format_ARGB32)
        combined.fill(Qt.GlobalColor.white)

        painter = QPainter(combined)

        # Przeskaluj wzorzec dokładnie tak jak podczas zapamiętywania
        remember_bg_width = display_info['image_width']
        remember_bg_height = display_info['image_height']
        final_scaled_bg = background_pixmap.scaled(
            remember_bg_width,
            remember_bg_height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        bg_x = display_info['offset_x']
        bg_y = display_info['offset_y']

        # Rysuj wzorzec
        painter.drawPixmap(bg_x, bg_y, final_scaled_bg)

        # Nałóż rysunek dziecka z przezroczystością
        painter.setOpacity(0.5)
        painter.drawImage(0, 0, user_image)

        # Ramka pokazująca gdzie był wzorzec
        painter.setOpacity(1.0)
        painter.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine))
        painter.drawRect(bg_x, bg_y, remember_bg_width, remember_bg_height)

        painter.end()
        return combined

    def _generate_heatmap(self, user_image: QImage) -> QImage:
        """Generuje mapę ciepła aktywności rysowania nałożoną na rysunek użytkownika."""
        width = user_image.width()
        height = user_image.height()

        # Tworzymy kopię rysunku dziecka jako tło
        result_img = user_image.copy()

        if not self._grid_visit_counts and not self._grid_overdraw_counts:
            return result_img

        # Obliczamy wymiary siatki
        cols = (width + self._grid_size - 1) // self._grid_size
        rows = (height + self._grid_size - 1) // self._grid_size

        # Tworzymy mały obraz reprezentujący siatkę dla uzyskania efektu wygładzenia (heatmapy)
        small_map = QImage(cols, rows, QImage.Format.Format_ARGB32)
        small_map.fill(Qt.GlobalColor.transparent)

        # Obliczamy połączony wynik dla każdej komórki
        all_cells = set(self._grid_visit_counts.keys()) | set(self._grid_overdraw_counts.keys())
        cell_scores = {}
        for cell in all_cells:
            visits = self._grid_visit_counts.get(cell, 0)
            overdraws = self._grid_overdraw_counts.get(cell, 0)
            # Powrót (nowa kreska) jest traktowany jako istotny sygnał (bonus 50 pkt)
            # oraz dodajemy liczbę nadrysowanych pikseli.
            cell_scores[cell] = (visits * 50) + overdraws

        if not cell_scores:
            return result_img

        max_score = max(cell_scores.values())
        if max_score == 0:
            max_score = 1

        # Wypełniamy mały obraz kolorami
        for (cx, cy), score in cell_scores.items():
            if cx >= cols or cy >= rows:
                continue

            # Skalowanie intensywności (0.0 - 1.0)
            intensity = score / max_score

            # Kolor od niebieskiego (zimny) do czerwonego (gorący)
            r = int(intensity * 255)
            b = int((1 - intensity) * 255)
            # Używamy nieco wyższej alfy (180), aby kolory były dobrze widoczne na tle rysunku
            color = QColor(r, 0, b, 180)

            small_map.setPixelColor(cx, cy, color)

        # Skalujemy małą mapę do oryginalnych rozmiarów z wygładzaniem (SmoothTransformation)
        # To stworzy ładne przejścia kolorystyczne zamiast ostrych krawędzi bloków.
        large_heatmap = small_map.scaled(
            width, height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Nakładamy wygładzoną mapę ciepła na rysunek dziecka
        painter = QPainter(result_img)
        painter.drawImage(0, 0, large_heatmap)
        painter.end()

        return result_img

    def _generate_velocity_profile_image(self) -> Optional[QImage]:
        """Generuje wykres profilu prędkości (prędkość w czasie) przy użyciu matplotlib."""
        if not self._current_velocities:
            return None

        try:
            import matplotlib.pyplot as plt
            import io

            # Używamy backendu Agg, aby nie otwierać okien GUI
            plt.switch_backend('Agg')

            plt.figure(figsize=(10, 5))
            plt.plot(self._current_velocities, color='blue', linewidth=1.5, label='Prędkość')

            # Dodanie opisów i siatki
            plt.title("Profil prędkości rysowania (Teoria Log-Normalna)", fontsize=14)
            plt.xlabel("Próbki (czas)", fontsize=12)
            plt.ylabel("Prędkość (px/s)", fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend()

            # Zapis do bufora w pamięci
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            plt.close() # Zamknięcie figury

            buf.seek(0)
            img = QImage.fromData(buf.getvalue())
            return img
        except Exception as e:
            print(f"Błąd podczas generowania wykresu profilu prędkości (matplotlib): {e}")
            traceback.print_exc()
            return None
