import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage

from db.service.ExaminationService import ExaminationService
from db.service.ImageService import ImageService
from db.service.PatientService import PatientService


class PdfGenerator:
    def __init__(self):
        self.patient_service = PatientService()
        self.examination_service = ExaminationService()
        self.image_service = ImageService()
        self.base_dir = Path.home() / "bvrt" / "outputs"

        # Rejestracja czcionki DejaVuSans (obsługa polskich znaków)
        font_path = os.path.join("assets", "fonts", "DejaVuSans.ttf")
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

    def _format_timedelta(self, td):
        if td is None:
            return "0 minut 0 sekund"
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes} minut {seconds} sekund"

    def _find_session_dir(self, patient_id, exam_id):
        pattern = f"test_*_{patient_id}_{exam_id}"
        matching_dirs = list(self.base_dir.glob(pattern))
        if matching_dirs:
            # Zwracamy najnowszy jeśli jest ich kilka (choć id badania powinno być unikalne)
            return sorted(matching_dirs, key=os.path.getmtime, reverse=True)[0]
        return None

    def _find_image_path(self, session_dir, index, patient_id, exam_id, is_overlay=False):
        suffix = "_overlay.png" if is_overlay else ".png"
        # index_timestamp_patient_id_examine_id.png
        # Ale uwaga: overlay ma format index_timestamp_patient_id_examine_id_overlay.png
        if is_overlay:
            pattern = f"{index}_*_{patient_id}_{exam_id}_overlay.png"
        else:
            # Musimy uważać, żeby nie złapać overlay.png przy szukaniu zwykłego .png
            pattern = f"{index}_*_{patient_id}_{exam_id}.png"

        matching_files = list(session_dir.glob(pattern))
        if matching_files:
            # Filtrowanie, aby wykluczyć overlay jeśli szukamy zwykłego obrazu
            if not is_overlay:
                matching_files = [f for f in matching_files if "_overlay.png" not in f.name]

            if matching_files:
                return sorted(matching_files, key=os.path.getmtime, reverse=True)[0]
        return None

    def generate_report(self, exam_id, output_path):
        examination = self.examination_service.get_examination_by_id(exam_id)
        if not examination:
            return False

        patient = self.patient_service.get_patient_by_id(examination.patient_id)
        if not patient:
            return False

        images = self.image_service.get_images_by_examine_id(exam_id)
        # Sortowanie po ID rysunku (najmniejsze to nr 1)
        images.sort(key=lambda x: x.id)

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Definicja stylów z użyciem nowej czcionki
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='DejaVuSans',
            fontSize=18,
            spaceAfter=12
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName='DejaVuSans',
            fontSize=14,
            spaceAfter=10
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName='DejaVuSans',
            fontSize=10
        )

        elements.append(Paragraph(f"Raport z badania - ID: {exam_id}", title_style))
        elements.append(Spacer(1, 12))

        # --- Tabela 1: Dane pacjenta ---
        elements.append(Paragraph("Dane pacjenta", heading_style))

        impairment_str = "TAK" if examination.visual_impairment else "NIE"
        if examination.visual_impairment and examination.impairment_description:
            impairment_str += f" - {examination.impairment_description}"

        patient_data = [
            ["Imię", patient.first_name],
            ["Nazwisko", patient.last_name],
            ["Płeć", patient.gender.value],
            ["Data urodzenia", str(patient.date_of_birth)],
            ["Ręka dominująca", patient.dominant_hand.value],
            ["Wada wzroku", impairment_str],
            ["Wykształcenie",
             f"{examination.education.value if examination.education else ''} - {examination.education_details.value if examination.education_details else ''}"],
            ["Wiek (lata)", str(examination.age_years)],
            ["Wiek (miesiące)", str(examination.age_months)],
            ["Wiek (dni)", str(examination.age_days)]
        ]

        patient_table = Table(patient_data, colWidths=[150, 300])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ]))
        elements.append(patient_table)
        elements.append(Spacer(1, 24))

        # --- Tabela 2: Dane badania ---
        elements.append(Paragraph("Dane badania", heading_style))

        exam_data = [
            ["Data badania", str(examination.date)],
            ["Czas całkowity badania", self._format_timedelta(examination.whole_time)],
            ["Średni czas na rysunek", self._format_timedelta(examination.avg_time)]
        ]

        exam_table = Table(exam_data, colWidths=[150, 300])
        exam_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ]))
        elements.append(exam_table)
        elements.append(Spacer(1, 24))

        # --- Tabela 3: Dane o rysunkach ---
        elements.append(Paragraph("Szczegóły rysunków (1-10)", heading_style))

        drawings_header = [
            "Nr", "Czas\nogólny", "Czas\nrys.", "Przerwy", "Śr. czas\nprzerw",
            "Powroty", "Szoro-\nwanie", "Zmiana\n150°", "Zmiana\n45°"
        ]
        drawings_data = [drawings_header]

        for idx, img in enumerate(images, start=1):
            if idx > 10: break

            drawings_data.append([
                str(idx),
                f"{img.duration_s:.2f}s",
                f"{img.actual_drawing_duration_s:.2f}s",
                str(img.interruptions_count),
                f"{img.avg_interruption_duration_s:.2f}s",
                str(img.revisit_count),
                "TAK" if img.shading_detected else "NIE",
                str(img.direction_reversal_count),  # >150 stopni
                str(img.direction_changes_count)  # 45 stopni
            ])

        drawings_table = Table(drawings_data, repeatRows=1)
        drawings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ]))
        elements.append(drawings_table)

        # --- Kolejne strony z rysunkami ---
        session_dir = self._find_session_dir(examination.patient_id, exam_id)

        for idx, img in enumerate(images, start=1):
            if idx > 10: break

            elements.append(PageBreak())

            # Nagłówek dla rysunku na nowej stronie
            elements.append(Paragraph(f"Rysunek nr {idx}", heading_style))

            # Tabela z danymi rysunku (jeden wiersz + nagłówek)
            single_drawing_data = [
                drawings_header,
                [
                    str(idx),
                    f"{img.duration_s:.2f}s",
                    f"{img.actual_drawing_duration_s:.2f}s",
                    str(img.interruptions_count),
                    f"{img.avg_interruption_duration_s:.2f}s",
                    str(img.revisit_count),
                    "TAK" if img.shading_detected else "NIE",
                    str(img.direction_reversal_count),
                    str(img.direction_changes_count)
                ]
            ]

            single_drawing_table = Table(single_drawing_data, colWidths=[30, 60, 60, 50, 60, 60, 60, 60, 60])
            single_drawing_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ]))
            elements.append(single_drawing_table)
            elements.append(Spacer(1, 12))

            if session_dir:
                img_path = self._find_image_path(session_dir, idx, examination.patient_id, exam_id, is_overlay=False)
                overlay_path = self._find_image_path(session_dir, idx, examination.patient_id, exam_id, is_overlay=True)

                # ReportLab Image
                max_width = 450
                max_height = 300

                if img_path and os.path.exists(img_path):
                    rl_img = RLImage(str(img_path))
                    # Zachowanie proporcji
                    aspect = rl_img.imageHeight / float(rl_img.imageWidth)
                    rl_img.drawWidth = max_width
                    rl_img.drawHeight = max_width * aspect
                    if rl_img.drawHeight > max_height:
                        rl_img.drawHeight = max_height
                        rl_img.drawWidth = max_height / aspect

                    elements.append(Paragraph("Oryginalny rysunek:", normal_style))
                    # Ramka dla obrazka (tabela z jedną komórką)
                    img_table = Table([[rl_img]], colWidths=[rl_img.drawWidth + 4])
                    img_table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 2),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ]))
                    elements.append(img_table)
                    elements.append(Spacer(1, 12))

                if overlay_path and os.path.exists(overlay_path):
                    rl_overlay = RLImage(str(overlay_path))
                    aspect = rl_overlay.imageHeight / float(rl_overlay.imageWidth)
                    rl_overlay.drawWidth = max_width
                    rl_overlay.drawHeight = max_width * aspect
                    if rl_overlay.drawHeight > max_height:
                        rl_overlay.drawHeight = max_height
                        rl_overlay.drawWidth = max_height / aspect

                    elements.append(Paragraph("Nałożenie na wzorzec (overlay):", normal_style))
                    # Ramka dla obrazka (tabela z jedną komórką)
                    overlay_table = Table([[rl_overlay]], colWidths=[rl_overlay.drawWidth + 4])
                    overlay_table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 2),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ]))
                    elements.append(overlay_table)

        doc.build(elements)
        return True
