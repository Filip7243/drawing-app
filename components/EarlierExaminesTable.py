from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QHeaderView, QSizePolicy
)

from components.StyledTextPopUp import StyledTextPopUp
from db.models import PreviousExaminationsDTO


class EarlierExaminesTable(QWidget):

    def __init__(self, table_data: list[PreviousExaminationsDTO], parent=None):
        super().__init__(parent)
        self.table_data: list[PreviousExaminationsDTO] = table_data
        self.popup = None  # referencja do aktywnego popupu

        self.table = QTableWidget()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.table)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._setup_ui()
        if self.table_data:
            self.set_data(self.table_data)
            self.table.resizeRowsToContents()
            self.table.setFixedHeight(
                self.table.verticalHeader().length()
            )

    # ----------------------------------------------------------------------
    # Pomocnicza metoda bezpiecznego ustawiania rowspan/colspan
    # ----------------------------------------------------------------------
    def _safe_set_span(self, row, col, rowspan, colspan):
        if rowspan > 1 or colspan > 1:
            self.table.setSpan(row, col, rowspan, colspan)

    # ----------------------------------------------------------------------
    # Inicjalizacja nagłówków i wyglądu
    # ----------------------------------------------------------------------
    def _setup_ui(self):
        table = self.table
        COL_NUM = 12  # kolumny: 1..12
        HEADER_ROWS = 2  # 2 wiersze nagłówków

        # Inicjalizacja tabeli (wiersze = 2 nagłówki + dane)
        table.setColumnCount(COL_NUM)
        table.setRowCount(HEADER_ROWS)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bfbfbf;
                font-size: 10.5pt;
                border: 1px solid #a0a0a0;
                border-radius: 6px;
                background-color: #f6f6f6;
            }
            QTableWidget::item {
                padding: 4px;
                background-color: transparent;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0063B1; }
            QPushButton:pressed { background-color: #004F8A; }
        """)

        # -----------------------------
        # Definicja nagłówków z rowspan/colspan
        # -----------------------------
        self._safe_set_span(0, 0, 2, 1)  # Data (rowspan=2)
        self._safe_set_span(0, 1, 1, 2)  # Odwzorowania (colspan=2)
        self._safe_set_span(0, 3, 1, 2)  # Czas (colspan=2)
        self._safe_set_span(0, 5, 1, 5)  # Typy błędów (colspan=5)
        self._safe_set_span(0, 10, 2, 1)  # Profil funkcji wzrokowo-przestrzennych (rowspan=2)
        self._safe_set_span(0, 11, 2, 1)  # Uwagi (rowspan=2)

        # Pierwszy wiersz nagłówków
        headers_row1 = [
            "Data", "Odwzorowania", "", "Czas (s)", "", "Typy błędów", "", "", "", "",
            "Profil funkcji\nwzrokowo-przestrzennych", "Uwagi"
        ]
        for c, text in enumerate(headers_row1):
            table.setItem(0, c, QTableWidgetItem(text))

        # Drugi wiersz nagłówków
        headers_row2 = [
            "", "Błędne", "Poprawne", "Śr.", "Cał.",
            "Pominięcia", "Deformacje", "Rotacje", "Przesunięcia", "Dodatki", "", ""
        ]
        for c, text in enumerate(headers_row2):
            table.setItem(1, c, QTableWidgetItem(text))

        # Stylowanie nagłówków
        for r in range(HEADER_ROWS):
            for c in range(COL_NUM):
                item = table.item(r, c)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setBackground(Qt.GlobalColor.lightGray)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Automatyczne dopasowanie szerokości
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    # ----------------------------------------------------------------------
    # Wypełnianie tabeli danymi z zewnątrz
    # ----------------------------------------------------------------------
    def set_data(self, data: list[PreviousExaminationsDTO]):
        """
        data: lista słowników np.:
        [
            {
                "data": "2025-10-30",
                "bledne": 2,
                "poprawne": 8,
                "czas_sredni": 1.2,
                "czas_cal": 12.4,
                "typy_bledow": [1, 0, 2, 1, 0],
                "profil": "W normie",
                "uwagi": "OK"
            },
            ...
        ]
        """
        self.table_data = data
        table = self.table
        start_row = 2  # po nagłówkach
        table.setRowCount(start_row + len(data))

        for i, row in enumerate(data):
            r = start_row + i
            # kolumna 1: Data
            self._set_cell(r, 0, str(row.examine_date))

            # kolumny 2–3: Odwzorowania
            self._set_cell(r, 1, str(row.failure_mappings), color=Qt.GlobalColor.red, bold=True)
            self._set_cell(r, 2, str(row.valid_mappings), color=QColor("#89c057"), bold=True)

            # kolumny 4–5: Czas
            self._set_cell(r, 3, str(round(row.avg_time.total_seconds(), 2)))
            self._set_cell(r, 4, str(round(row.whole_time.total_seconds(), 2)))

            # kolumny 6–10: Typy błędów
            # TODO: powiększyć tabele o bledy wzglednej wielkosci
            self._set_cell(r, 5, str(row.pominiecia))
            self._set_cell(r, 6, str(row.znieksztalcenia))
            self._set_cell(r, 7, str(row.perserwacje))
            self._set_cell(r, 8, str(row.rotacje))
            self._set_cell(r, 9, str(row.przemieszczenia))

            # kolumna 11: Profil funkcji
            self._set_cell(r, 10, str(row.result), wrap=True)

            # kolumna 12: Uwagi (przycisk)
            btn = QPushButton("Uwagi")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self.on_remarks_clicked(idx))
            table.setCellWidget(r, 11, btn)

            # ----------------------------------------------------------------------
            # Pomocnicza metoda do tworzenia komórek
            # ----------------------------------------------------------------------

    def _set_cell(self, row, col, text, bold=False, wrap=False, color=None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = item.font()
        font.setBold(bold)
        item.setFont(font)

        if color:
            # color może być np. Qt.GlobalColor.red lub QColor("#ff0000")
            item.setForeground(QBrush(color))

        if wrap:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setToolTip(text)
        self.table.setItem(row, col, item)

    # ----------------------------------------------------------------------
    # Obsługa kliknięcia przycisku "Uwagi"
    # ----------------------------------------------------------------------
    def on_remarks_clicked(self, index):
        # Zamknij poprzedni popup, jeśli istnieje
        if self.popup:
            self.popup.close()
            self.popup = None

        # Pobierz dane dla tego wiersza
        print("INDEX:", index)
        print("self.table_data:", self.table_data)
        row_data = self.table_data[index] if index < len(self.table_data) else []
        print("ROW_DATA:", row_data)
        uwagi_text = row_data.comment

        # Utwórz nowy popup
        self.popup = StyledTextPopUp(
            f"Uwagi",
            uwagi_text,
            parent=self
        )

        # Wyświetl popup
        self.popup.show()

        # Wycentruj popup na ekranie
        screen = self.popup.screen().geometry()
        popup_size = self.popup.size()
        x = (screen.width() - popup_size.width()) // 2
        y = (screen.height() - popup_size.height()) // 2
        self.popup.move(x, y)

    # ----------------------------------------------------------------------
    # Override mousePressEvent - zamknij popup przy kliknięciu poza nim
    # ----------------------------------------------------------------------
    def mousePressEvent(self, event):
        if self.popup and self.popup.isVisible():
            # Sprawdź czy kliknięcie było poza popupem
            popup_global_rect = self.popup.geometry()
            popup_global_rect.moveTopLeft(self.popup.mapToGlobal(self.popup.rect().topLeft()))

            if not popup_global_rect.contains(event.globalPosition().toPoint()):
                self.popup.close()
                self.popup = None
        super().mousePressEvent(event)
