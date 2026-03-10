from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QHeaderView, QSizePolicy, QFileDialog, QMessageBox
)
from pdf.PdfGenerator import PdfGenerator

class LatestExaminationsTable(QWidget):
    def __init__(self, table_data: list, parent=None):
        super().__init__(parent)
        self.table_data = table_data
        self.pdf_generator = PdfGenerator()

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

    def _on_generate_clicked(self, row_index):
        exam_id = self.table_data[row_index]['exam_id']
        patient_name = f"{self.table_data[row_index]['first_name']}_{self.table_data[row_index]['last_name']}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz raport PDF",
            f"BVRT_Raport_{patient_name}_{exam_id}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                success = self.pdf_generator.generate_report(exam_id, file_path)
                if success:
                    QMessageBox.information(self, "Sukces", f"Raport został wygenerowany pomyślnie:\n{file_path}")
                else:
                    QMessageBox.warning(self, "Błąd", "Nie udało się wygenerować raportu. Sprawdź czy dane badania istnieją.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd krytyczny", f"Wystąpił błąd podczas generowania raportu:\n{str(e)}")

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
            btn.clicked.connect(lambda checked, r=i: self._on_generate_clicked(r))
            table.setCellWidget(i, 4, btn)
            
        table.resizeRowsToContents()
