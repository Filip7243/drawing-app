from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QHeaderView, QSizePolicy
)


class EarlierExaminesTable(QWidget):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.data = data or []

        self.table = QTableWidget()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.table)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._setup_ui()
        if self.data:
            self.set_data(self.data)
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
                background-color: white;
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
    def set_data(self, data):
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
        table = self.table
        start_row = 2  # po nagłówkach
        table.setRowCount(start_row + len(data))

        for i, row in enumerate(data):
            r = start_row + i
            # kolumna 1: Data
            self._set_cell(r, 0, str(row.get("data", "")))

            # kolumny 2–3: Odwzorowania
            self._set_cell(r, 1, str(row.get("bledne", "")), color=Qt.GlobalColor.red, bold=True)
            self._set_cell(r, 2, str(row.get("poprawne", "")), color=QColor("#89c057"), bold=True)

            # kolumny 4–5: Czas
            self._set_cell(r, 3, str(row.get("czas_sredni", "")))
            self._set_cell(r, 4, str(row.get("czas_cal", "")))

            # kolumny 6–10: Typy błędów
            typy = row.get("typy_bledow", [0, 0, 0, 0, 0])
            for j in range(5):
                self._set_cell(r, 5 + j, str(typy[j]))

            # kolumna 11: Profil funkcji
            self._set_cell(r, 10, str(row.get("profil", "")), wrap=True)

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
    # Placeholder dla akcji przycisku
    # ----------------------------------------------------------------------
    def on_remarks_clicked(self, index):
        print(f"Kliknięto przycisk 'Uwagi' w wierszu {index + 1}")
