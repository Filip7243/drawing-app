import unittest
import sys
from unittest.mock import MagicMock, patch

# Mockowanie PyQt6 zanim TestMetrics zostanie zaimportowane
mock_pyqt6 = MagicMock()
sys.modules['PyQt6'] = mock_pyqt6
sys.modules['PyQt6.QtCore'] = MagicMock()
sys.modules['PyQt6.QtGui'] = MagicMock()

from pathlib import Path
from controllers.TestMetrics import TestMetrics
from db.models import TestMetaData


class TestTestMetricsFix(unittest.TestCase):
    def setUp(self):
        # Mockujemy baze danych i serwisy
        with patch('controllers.TestMetrics.ImageRepository'), \
                patch('controllers.TestMetrics.ExaminationService'):
            self.metrics = TestMetrics(base_dir=Path("./test_outputs"))
            self.metrics.test_meta_data(TestMetaData(examine_id=1, patient_id=1))

    def test_end_test_success(self):
        # Testujemy czy end_test nie rzuca juz KeyError i ZeroDivisionError
        with patch('controllers.TestMetrics.perf_counter', side_effect=[10.0, 25.0]):
            self.metrics.start_test()  # 10.0

            # Symulujemy zakonczenie rysowania, aby miec jakis rekord
            mock_image = MagicMock()
            with patch.object(self.metrics, '_generate_overlay'), \
                    patch.object(self.metrics, '_generate_heatmap'), \
                    patch('controllers.TestMetrics.image_to_bytes'):
                self.metrics.start_drawing()
                self.metrics.finish_drawing(mock_image)

            # Teraz wolamy end_test (uzyje 25.0)
            summary = self.metrics.end_test()

            self.assertEqual(summary["total_duration_s"], 15.0)
            self.assertIn("drawings", summary)
            self.assertEqual(len(summary["drawings"]), 1)

    def test_end_test_empty_records(self):
        # Testujemy czy end_test nie rzuca ZeroDivisionError przy braku rysunkow
        with patch('controllers.TestMetrics.perf_counter', side_effect=[10.0, 20.0]):
            self.metrics.start_test()  # 10.0
            summary = self.metrics.end_test()  # 20.0

            self.assertEqual(summary["total_duration_s"], 10.0)
            self.assertEqual(len(summary["drawings"]), 0)


if __name__ == "__main__":
    unittest.main()
