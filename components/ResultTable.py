from datetime import timedelta

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QHeaderView, QSizePolicy, QDialog
)
from PySide6.QtWidgets import QSlider

from db.models import ImageTableDataSummary
from db.service.ImageService import ImageService

COL_NUM = 9
ROW_NUM = 13


class ResultTable(QWidget):
    imageService = ImageService()

    def __init__(self, examine_id=None, parent=None, summary=None):
        super().__init__(parent)
        self.table = QTableWidget(ROW_NUM, COL_NUM)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.table)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        print("GETTING DATA IMAGE:")
        self.data = self.imageService.get_images_table_summary_by_examine_id(examine_id) or []
        print("DATA FOUND: ", self.data)
        self.summary = summary
        self._setup_ui()
        if self.data:
            try:
                self.set_data(self.data)
            except Exception as e:
                print("ex", e)

    def _safe_set_span(self, row: int, col: int, rowspan: int, colspan: int):
        """Bezpieczne ustawienie spanów, unikające błędu QTableView::setSpan"""
        if rowspan > 1 or colspan > 1:
            self.table.setSpan(row, col, rowspan, colspan)

    def _setup_ui(self):
        table = self.table
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bfbfbf;
                font-size: 11pt;
                border: 2px solid #a0a0a0;
                border-radius: 6px;
                background-color: #f6f6f6;
            }
            QTableWidget::item {
                padding: 4px;
                background-color: transparent;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)

        # -----------------------------
        # Tworzenie nagłówków z rowspan/colspan
        # -----------------------------
        self._safe_set_span(0, 0, 2, 1)  # Rys. (rowspan 2)
        self._safe_set_span(0, 1, 2, 1)  # Poprawne? (rowspan 2)
        self._safe_set_span(0, 2, 2, 1)  # Czas (rowspan 2)
        self._safe_set_span(0, 3, 1, 5)  # Typ błędu (colspan 5)
        self._safe_set_span(0, 8, 2, 1)  # Pokaż (rowspan 2)

        table.setItem(0, 0, QTableWidgetItem("Rys."))
        table.setItem(0, 1, QTableWidgetItem("Poprawne?"))
        table.setItem(0, 2, QTableWidgetItem("Czas (s)"))
        table.setItem(0, 3, QTableWidgetItem("Typ błędu"))
        table.setItem(0, 8, QTableWidgetItem("Pokaż"))

        # Wiersz 1 (drugi nagłówek)
        headers = ["Pominięcia", "Deformacje", "Rotacje", "Przesunięcia", "Dodatki"]
        for i, header in enumerate(headers):
            table.setItem(1, 3 + i, QTableWidgetItem(header))

        # -----------------------------
        # Formatowanie komórek nagłówków
        # -----------------------------
        for r in range(2):
            for c in range(COL_NUM):
                item = table.item(r, c)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setBackground(Qt.GlobalColor.lightGray)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

        # Ustaw szerokości kolumn
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

    # -----------------------------
    #  Wypełnianie tabeli danymi
    # -----------------------------
    def set_data(self, data: list[ImageTableDataSummary]):
        table = self.table
        row_index = 2
        correct_count = 0
        incorrect_count = 0

        tick_path = "assets:icons/tick.svg"
        cross_path = "assets:icons/cross.svg"

        for row in data:
            # Kolumna 0: Rys.
            self._set_cell(row_index, 0, str(row.idx))

            # Kolumna 1: Poprawne?
            is_valid = row.is_valid
            icon_path = tick_path if is_valid else cross_path

            icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(
                pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon_widget = QWidget()
            layout = QHBoxLayout(icon_widget)
            layout.addWidget(icon_label)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            table.setCellWidget(row_index, 1, icon_widget)

            if is_valid:
                correct_count += 1
            else:
                incorrect_count += 1

            # Kolumna 2: czas
            self._set_cell(row_index, 2, str(round(row.time.total_seconds(), 2)))

            # Kolumny 3–7: błędy
            errors = row.failures
            for j, val in enumerate(errors):
                self._set_cell(row_index, 3 + j, str(val))

            btn = QPushButton("Pokaż")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=row.idx: self.on_show_clicked(idx))
            table.setCellWidget(row_index, 8, btn)

            row_index += 1

        # -----------------------------
        # Wiersz podsumowania
        # -----------------------------
        summary_row = row_index
        self._safe_set_span(summary_row, 0, 1, 1)
        self._set_cell(summary_row, 0, "Podsumowanie", bold=True)
        summary_text = f"{correct_count} / {incorrect_count}"
        self._set_cell(summary_row, 1, summary_text, bold=True)

        total_time = sum((item.time for item in data), timedelta())
        total_seconds = round(total_time.total_seconds(), 2)
        self._set_cell(summary_row, 2, str(total_seconds), bold=True)

        total_failures0 = sum((item.failures[0] for item in data), 0)
        total_failures1 = sum((item.failures[1] for item in data), 0)
        total_failures2 = sum((item.failures[2] for item in data), 0)
        total_failures3 = sum((item.failures[3] for item in data), 0)
        total_failures4 = sum((item.failures[4] for item in data), 0)
        self._set_cell(summary_row, 3, str(total_failures0), bold=True)
        self._set_cell(summary_row, 4, str(total_failures1), bold=True)
        self._set_cell(summary_row, 5, str(total_failures2), bold=True)
        self._set_cell(summary_row, 6, str(total_failures3), bold=True)
        self._set_cell(summary_row, 7, str(total_failures4), bold=True)

    def _set_cell(self, row, col, text, bold=False):
        """Pomocnicza funkcja ustawiająca komórkę z wyrównaniem i pogrubieniem"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = item.font()
        font.setBold(bold)
        item.setFont(font)
        self.table.setItem(row, col, item)

    def on_show_clicked(self, row_index):
        """
        Wyświetla nałożenie rysunku dziecka i obrazu wzorcowego.
        Używa zapisanych informacji z display_info.
        """
        # === 1. Pobierz dane ===
        drawing_data = self.data[row_index - 1]

        # Wczytaj rysunek dziecka
        user_pixmap = QPixmap()
        user_pixmap.loadFromData(drawing_data.content)

        if user_pixmap.isNull():
            print("Nie udało się wczytać rysunku dziecka.")
            return

        canvas_width = user_pixmap.width()
        canvas_height = user_pixmap.height()
        print(f"Canvas (DrawingPage): {canvas_width}x{canvas_height}")

        # === 2. Wczytaj obraz wzorcowy ===
        background_path = f"assets:img/figures/bvrt_c_{row_index}.png"
        background_pixmap = QPixmap(background_path)

        if background_pixmap.isNull():
            print(f"Nie udało się wczytać obrazu wzorcowego: {background_path}")
            return

        print(f'======================self.summary: {self.summary}')
        # === 3. Użyj zapisanych informacji o wyświetlaniu ===
        display_info = self.summary['drawings'][row_index - 1]['display_info']

        # === 4. Odtwórz dokładną transformację z RememberFigurePage ===

        # Przeskaluj wzorzec dokładnie tak jak podczas zapamiętywania
        remember_bg_width = display_info['image_width']
        remember_bg_height = display_info['image_height']

        final_scaled_bg = background_pixmap.scaled(
            remember_bg_width,
            remember_bg_height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Pozycja wzorca podczas zapamiętywania (współrzędne okna)
        bg_x = display_info['offset_x']
        bg_y = display_info['offset_y']

        print(f"Original remember window: {display_info['window_width']}x{display_info['window_height']}")
        print(f"Final position on drawing canvas: ({bg_x}, {bg_y})")
        print(f"Final scaled size: {remember_bg_width}x{remember_bg_height}")

        # === 6. Utwórz obraz wynikowy ===
        combined_pixmap = QPixmap(canvas_width, canvas_height)
        combined_pixmap.fill(Qt.GlobalColor.white)

        painter = QPainter(combined_pixmap)

        # Rysuj wzorzec
        painter.drawPixmap(bg_x, bg_y, final_scaled_bg)

        # Nałóż rysunek dziecka z przezroczystością
        painter.setOpacity(0.5)
        painter.drawPixmap(0, 0, user_pixmap)

        # Ramka pokazująca gdzie był wzorzec
        painter.setOpacity(1.0)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine))
        painter.drawRect(bg_x, bg_y, remember_bg_width, remember_bg_height)

        painter.end()

        # === 7. Wyświetl z suwakiem przezroczystości ===
        dialog = QDialog()
        dialog.setWindowTitle(f"Porównanie - Rysunek {row_index}")

        info_label = QLabel(
            f"Czerwona ramka = pozycja wzorca podczas zapamiętywania\n"
            f"Przezroczysty obraz = rysunek dziecka\n"
        )
        info_label.setStyleSheet("background-color: #ffffcc; padding: 10px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image_label = QLabel()
        image_label.setPixmap(combined_pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(info_label)
        layout.addWidget(image_label)

        dialog.setLayout(layout)
        dialog.showMaximized()
        dialog.exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        total_width = self.table.viewport().width()
        proportions = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        total_prop = sum(proportions)
        for i, prop in enumerate(proportions):
            self.table.setColumnWidth(i, int(total_width * prop / total_prop))
