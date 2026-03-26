import os
from pathlib import Path
from datetime import datetime
import xlsxwriter
from db.service.ExaminationService import ExaminationService
from db.service.ImageService import ImageService
from db.service.PatientService import PatientService

class ExcelGenerator:
    def __init__(self):
        self.patient_service = PatientService()
        self.examination_service = ExaminationService()
        self.image_service = ImageService()
        self.base_dir = Path.home() / "bvrt" / "outputs"
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True, exist_ok=True)

    def generate_global_report(self, output_path=None):
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.base_dir / f"global_bvrt_report_{timestamp}.xlsx"

        workbook = xlsxwriter.Workbook(str(output_path))
        worksheet = workbook.add_worksheet("BVRT Global Report")

        # Formaty
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        date_format = workbook.add_format({
            'border': 1,
            'num_format': 'yyyy-mm-dd',
            'align': 'center',
            'valign': 'vcenter'
        })

        # Nagłówki
        headers = [
            "ID Pacjenta", "Data badania", "Płeć K/M", "Wiek", "Ręka dominująca", "Wada wzroku tak/nie",
            "Imię i Nazwisko", "Poprawne", "Błędne",
            "Pominiecie", "Zniekształcenie", "Perserwacje", "Rotacje", "Przemieszczenie", "Błędy względnej wielkości",
            "Wynik", "Uwagi"
        ]

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            if col == 14: # "Błędy względnej wielkości"
                worksheet.set_column(col, col, 25)
            elif col == 6: # "Imię i Nazwisko"
                worksheet.set_column(col, col, 25)
            elif col == 15: # "Wynik"
                worksheet.set_column(col, col, 25)
            elif col == 16: # "Uwagi"
                worksheet.set_column(col, col, 30)
            else:
                worksheet.set_column(col, col, 20)

        # Formaty kolorystyczne dla wyników
        green_format = workbook.add_format({
            'bg_color': '#C6EFCE',
            'font_color': '#006100',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        orange_format = workbook.add_format({
            'bg_color': '#FFEB9C',
            'font_color': '#9C5700',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        red_format = workbook.add_format({
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        examinations = self.examination_service.get_all_examinations()
        
        row_idx = 1
        for exam in examinations:
            patient = self.patient_service.get_patient_by_id(exam.patient_id)
            if not patient:
                continue
            
            # 0: ID Pacjenta
            worksheet.write(row_idx, 0, patient.id, cell_format)
            # 1: Data badania
            worksheet.write(row_idx, 1, str(exam.date), date_format)
            # 2: Płeć K/M
            gender_map = {"MALE": "M", "FEMALE": "K"}
            gender_val = patient.gender.name if hasattr(patient.gender, 'name') else str(patient.gender)
            worksheet.write(row_idx, 2, gender_map.get(gender_val, gender_val), cell_format)
            # 3: Wiek
            worksheet.write(row_idx, 3, f"{exam.age_years}l {exam.age_months}m", cell_format)
            # 4: Ręka dominująca
            hand_map = {"RIGHT": "Prawa", "LEFT": "Lewa"}
            hand_val = patient.dominant_hand.name if hasattr(patient.dominant_hand, 'name') else str(patient.dominant_hand)
            worksheet.write(row_idx, 4, hand_map.get(hand_val, hand_val), cell_format)
            # 5: Wada wzroku tak/nie
            worksheet.write(row_idx, 5, "TAK" if exam.visual_impairment else "NIE", cell_format)
            # 6: Imię i Nazwisko
            worksheet.write(row_idx, 6, f"{patient.first_name} {patient.last_name}", cell_format)
            
            # 7: Poprawne (puste do wypełnienia)
            worksheet.write(row_idx, 7, "", cell_format)
            # 8: Błędne (puste do wypełnienia)
            worksheet.write(row_idx, 8, "", cell_format)
            
            # 9-14: Typy błędów (puste do wypełnienia)
            for col in range(9, 15):
                worksheet.write(row_idx, col, "", cell_format)
            
            # 15: Wynik (Formuła IF na podstawie kolumny "Błędne" - indeks 8)
            # Zakres	Informacje
            # 1-5	niskie ryzyko dysleksji
            # 6-7	przecietny poziom zaburzenia
            # 8>	wysoki poziom zaburzenia
            
            cell_err = xlsxwriter.utility.xl_rowcol_to_cell(row_idx, 8)
            formula = (f'=IF({cell_err}="", "", '
                       f'IF({cell_err}<=5, "niskie ryzyko dysleksji", '
                       f'IF({cell_err}<=7, "przecietny poziom zaburzenia", "wysoki poziom zaburzenia")))')
            
            worksheet.write_formula(row_idx, 15, formula, cell_format)
            # 16: Uwagi (puste do wypełnienia)
            worksheet.write(row_idx, 16, "", cell_format)
            
            # Dodanie formatowania warunkowego dla kolumny Wynik (indeks 15) na podstawie kolumny Błędne (indeks 8)
            # Formuła odnosi się do komórki w tym samym wierszu
            worksheet.conditional_format(row_idx, 15, row_idx, 15, {
                'type':     'formula',
                'criteria': f'=AND(ISNUMBER({cell_err}), {cell_err}>=1, {cell_err}<=5)',
                'format':   green_format
            })
            worksheet.conditional_format(row_idx, 15, row_idx, 15, {
                'type':     'formula',
                'criteria': f'=AND(ISNUMBER({cell_err}), {cell_err}>=6, {cell_err}<=7)',
                'format':   orange_format
            })
            worksheet.conditional_format(row_idx, 15, row_idx, 15, {
                'type':     'formula',
                'criteria': f'=AND(ISNUMBER({cell_err}), {cell_err}>=8)',
                'format':   red_format
            })
            
            row_idx += 1

        workbook.close()
        return str(output_path)
