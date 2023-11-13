"""Tests for the Needs class."""

from unittest.mock import patch, Mock
import pandas as pd
import pytest
from facs.base.needs import Needs

# pylint: disable=redefined-outer-name


TEST_DATA = """location,office,school,market
               0,40,50,60
               1,30,35,45"""

correct_dataframe = pd.DataFrame(
    {"office": [40, 30], "school": [50, 35], "market": [60, 45]}, index=[0, 1]
)

correct_building_types = ["office", "school", "market"]

incorrect_building_types = ["office", "school", "hospital"]


@patch("os.path.exists")
@patch("os.path.isfile")
@patch("os.path.splitext")
@patch("pandas.read_csv")
def needs_instance(mock_read_csv, mock_splitext, mock_isfile, mock_exists) -> Needs:
    """Creates an instance of the Needs class to be used by other tests."""

    mock_exists.return_value = True
    mock_isfile.return_value = True
    mock_splitext.return_value = ("test_file", ".csv")
    mock_read_csv.return_value = correct_dataframe.copy()
    needs_instance = Needs("test_file.csv", correct_building_types)
    return needs_instance


@patch("os.path.exists")
@patch("os.path.isfile")
@patch("os.path.splitext")
@patch("pandas.read_csv")
def failing_needs_instance(
    mock_read_csv, mock_splitext, mock_isfile, mock_exists
) -> Needs:
    """Tries to creates an incorrect instance of the Needs class to be used by other tests."""

    mock_exists.return_value = True
    mock_isfile.return_value = True
    mock_splitext.return_value = ("test_file", ".csv")
    mock_read_csv.return_value = correct_dataframe.copy()
    Needs("test_file.csv", incorrect_building_types)  # This line should fail


@patch("os.path.exists")
def test_file_initialization_nonexistent(mock_exists):
    """Tests failing Needs initialization with a nonexistent file."""

    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError):
        Needs("nonexistent.csv", ["office", "school", "market"])


@patch("os.path.exists")
@patch("os.path.isfile")
def test_file_initialization_not_a_file(mock_isfile, mock_exists):
    """Tests failing Needs initialization with non-file obeject."""

    mock_exists.return_value = True
    mock_isfile.return_value = False
    with pytest.raises(ValueError):
        Needs("directory_path", ["office", "school", "market"])


@patch("os.path.exists")
@patch("os.path.isfile")
@patch("os.path.splitext")
def test_file_initialization_invalid_extension(mock_splitext, mock_isfile, mock_exists):
    """Tests failing Needs initialization with wrong extension."""

    mock_exists.return_value = True
    mock_isfile.return_value = True
    mock_splitext.return_value = ("test_file", ".txt")
    with pytest.raises(ValueError):
        Needs("invalid_file.txt", ["office", "school", "market"])


def test_file_initialization_invalid_building_types():
    """Tests failing Needs initialization with wrong building types."""

    with pytest.raises(ValueError):
        failing_needs_instance()  # pylint: disable=no-value-for-parameter


def test_needs_object_creation():
    """Tests the needs object creation."""

    needs = needs_instance()  # pylint: disable=no-value-for-parameter
    assert needs.needs.shape == (2, 3)
    assert "school" in needs.needs.columns
    assert needs.needs["school"].dtype == int
    assert set(needs.needs.columns) == {"office", "school", "market"}


def test_get_needs():
    """Test the get_needs method."""

    needs = needs_instance()  # pylint: disable=no-value-for-parameter

    mock_person_1 = Mock(
        age=1, hospitalised=False, work_from_home=False, school_from_home=False
    )
    mock_person_2 = Mock(
        age=1, hospitalised=True, work_from_home=False, school_from_home=False
    )
    mock_person_3 = Mock(
        age=1, hospitalised=False, work_from_home=True, school_from_home=False
    )
    mock_person_4 = Mock(
        age=1, hospitalised=True, work_from_home=True, school_from_home=False
    )
    mock_person_5 = Mock(
        age=1, hospitalised=False, work_from_home=False, school_from_home=True
    )
    mock_person_6 = Mock(
        age=1, hospitalised=True, work_from_home=False, school_from_home=True
    )
    mock_person_7 = Mock(
        age=1, hospitalised=False, work_from_home=True, school_from_home=True
    )
    mock_person_8 = Mock(
        age=1, hospitalised=True, work_from_home=True, school_from_home=True
    )

    assert needs.get_needs(mock_person_1) == [30, 26, 45]
    assert needs.get_needs(mock_person_2) == [0, 5040, 0, 0, 0, 0, 0]
    assert needs.get_needs(mock_person_3) == [0, 26, 45]
    assert needs.get_needs(mock_person_4) == [0, 5040, 0, 0, 0, 0, 0]
    assert needs.get_needs(mock_person_5) == [30, 0, 45]
    assert needs.get_needs(mock_person_6) == [0, 5040, 0, 0, 0, 0, 0]
    assert needs.get_needs(mock_person_7) == [0, 0, 45]
    assert needs.get_needs(mock_person_8) == [0, 5040, 0, 0, 0, 0, 0]


def test_scale_needs():
    """Test the scale_needs method."""

    needs = needs_instance()  # pylint: disable=no-value-for-parameter

    needs.scale_needs("office", 0.5)
    assert needs.needs["office"].sum() == 35
    needs.scale_needs("school", 0.5)
    assert needs.needs["school"].sum() == 31.5
    needs.scale_needs("market", 0.5)
    assert needs.needs["market"].sum() == 52.5

    with pytest.raises(ValueError):
        needs.scale_needs("hospital", 0.5)

    with pytest.raises(ValueError):
        needs.scale_needs("office", -0.5)
