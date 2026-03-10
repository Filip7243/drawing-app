from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QHeaderView, QSizePolicy
)

class LatestExaminationsTable(QWidget):
    def __init__(self, table_data: list, parent=None):
        super().__init__(parent)
        self.table_data = table_data

        self.table = QTableWidget()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.table)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._setup_ui()
        if self.table_data:
            self.set_data(self.table_data)

    def _setup_ui(self):
        table = self.table
        columns = ["ID pacjenta", "ID badania", "Imię i Nazwisko", "Data badania", "Akcja"]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bfbfbf;
                font-size: 11pt;
                border: 1px solid #a0a0a0;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 6px;
                border: 1px solid #bfbfbf;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0063B1; }
            QPushButton:pressed { background-color: #004F8A; }
        """)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def set_data(self, data: list):
        self.table_data = data
        table = self.table
        table.setRowCount(len(data))

        for i, row in enumerate(data):
            # ID pacjenta
            item_p_id = QTableWidgetItem(str(row['patient_id']))
            item_p_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(i, 0, item_p_id)

            # ID badania
            item_e_id = QTableWidgetItem(str(row['exam_id']))
            item_e_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(i, 1, item_e_id)

            # Imię i Nazwisko
            full_name = f"{row['first_name']} {row['last_name']}"
            item_name = QTableWidgetItem(full_name)
            item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(i, 2, item_name)

            # Data badania
            item_date = QTableWidgetItem(str(row['exam_date']))
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(i, 3, item_date)

            # Przycisk Generuj
            btn = QPushButton("Generuj")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Na razie bez implementacji generowania raportu
            table.setCellWidget(i, 4, btn)
            
        table.resizeRowsToContents()
