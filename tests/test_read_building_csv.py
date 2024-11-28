import pytest
from unittest.mock import Mock, mock_open, patch
import csv

from facs.readers.read_building_csv import read_building_csv


def test_read_building_csv_missing_file():
    e = Mock()
    csvfile = "fakepath/fakefile.csv"
    with patch('builtins.open', mock_open()) as mocked_file:
        mocked_file.side_effect = FileNotFoundError()
        with pytest.raises(FileNotFoundError):
            read_building_csv(e, csvfile)
            
