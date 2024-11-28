import unittest
from unittest.mock import MagicMock
from datetime import datetime
import io
import sys

from facs.readers.read_cases_csv import read_cases_csv, subtract_dates

class TestReadCasesCSV(unittest.TestCase):
    def test_subtract_dates(self):
        self.assertEqual(subtract_dates("3/20/2020", "3/18/2020"), 2)
        self.assertEqual(subtract_dates("3/18/2020", "3/20/2020"), -2)

    def test_read_cases_csv(self):
        # Simulate the Ecosystem object
        e = MagicMock()
        e.disease.period_to_hospitalisation = 5
        e.disease.recovery_period = 14

        # Create a sample CSV content
        sample_csv_data = """x,y,age,date
-0.338880986,51.5628624,27,3/20/2020
-0.338880986,51.5628624,27,3/17/2020
"""

        # Use io.StringIO to simulate file reading
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=sample_csv_data)):
            with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                read_cases_csv(e, "dummy_path.csv")
                # Check if the correct number of infections are added
                self.assertEqual(e.add_infection.call_count, 1)
                self.assertEqual(e.add_infections.call_count, 1)
                # Check output messages
                output = mock_stdout.getvalue()
                self.assertIn("Using start date 3/18/2020 with 17 infections initially.", output)

    def test_read_cases_csv_with_invalid_data(self):
        e = MagicMock()
        e.disease.period_to_hospitalisation = 5
        e.disease.recovery_period = 14

        # Simulate CSV with invalid date format
        invalid_csv_data = """x,y,age,date
-0.338880986,51.5628624,27,03-20-2020
"""
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=invalid_csv_data)):
            with self.assertRaises(ValueError):
                read_cases_csv(e, "dummy_path.csv")

if __name__ == '__main__':
    unittest.main()
