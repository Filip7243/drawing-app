from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QHeaderView, QSizePolicy
)

COL_NUM = 9
ROW_NUM = 13


class ResultTable(QWidget):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.table = QTableWidget(ROW_NUM, COL_NUM)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.table)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.data = data or []
        self._setup_ui()
        if data:
            self.set_data(data)

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
    def set_data(self, data):
        table = self.table
        row_index = 2
        correct_count = 0
        incorrect_count = 0

        tick_path = "assets:icons/tick.svg"
        cross_path = "assets:icons/cross.svg"

        for i, row in enumerate(data):
            # Kolumna 0: Rys.
            self._set_cell(row_index, 0, str(row.get("rys", i + 1)))

            # Kolumna 1: Poprawne?
            is_ok = row.get("poprawne", False)
            icon_path = tick_path if is_ok else cross_path

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

            if is_ok:
                correct_count += 1
            else:
                incorrect_count += 1

            # Kolumna 2: czas
            self._set_cell(row_index, 2, str(row.get("czas", "")))

            # Kolumny 3–7: błędy
            errors = row.get("bledy", [0, 0, 0, 0, 0])
            for j, val in enumerate(errors):
                self._set_cell(row_index, 3 + j, str(val))

            # Kolumna 8: przycisk "Pokaż"
            btn = QPushButton("Pokaż")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self.on_show_clicked(idx))
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
        self._set_cell(summary_row, 2, "200", bold=True)
        self._set_cell(summary_row, 3, "10", bold=True)
        self._set_cell(summary_row, 4, "10", bold=True)
        self._set_cell(summary_row, 5, "10", bold=True)
        self._set_cell(summary_row, 6, "10", bold=True)
        self._set_cell(summary_row, 7, "10", bold=True)

    def _set_cell(self, row, col, text, bold=False):
        """Pomocnicza funkcja ustawiająca komórkę z wyrównaniem i pogrubieniem"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = item.font()
        font.setBold(bold)
        item.setFont(font)
        self.table.setItem(row, col, item)

    def on_show_clicked(self, row_index):
        print(f"Kliknięto przycisk 'Pokaż' w wierszu {row_index + 1}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        total_width = self.table.viewport().width()
        proportions = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        total_prop = sum(proportions)
        for i, prop in enumerate(proportions):
            self.table.setColumnWidth(i, int(total_width * prop / total_prop))
