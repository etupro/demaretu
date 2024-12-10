import pytest
import requests
import pandas as pd
from unittest.mock import patch, MagicMock
from cleaner._transform import get_postal_code, add_cities, \
    change_domaine, add_spe, add_level, add_id, transform_data
from hashlib import md5

# Mock logger to avoid real logging during tests
from cleaner._transform import logger
logger.disabled = True

# Mock class with the required `self.df` for DataFrame-dependent functions
class MockDataFrameClass:
    def __init__(self, df):
        self.df = df
    from cleaner._transform import get_postal_code, add_cities, \
    change_domaine, add_spe, add_level, add_id, transform_data
    get_postal_code = staticmethod(get_postal_code)

# -----------------------
# Tests for get_postal_code
# -----------------------
@patch("requests.get")
def test_get_postal_code(mock_get):
    # Mock API response
    mock_response = MagicMock()
    mock_response.content = b'{"features":[{"properties":{"postcode":"75001"}}]}'
    mock_get.return_value = mock_response

    # Test with single city
    result = get_postal_code("Paris")
    assert result == ["75001"]

    # Test with multiple cities
    result = get_postal_code("Paris,Lyon")
    assert result == ["75001", "75001"]  # Mocked response for all calls

    # Test with invalid city
    mock_response.content = b'{}'
    result = get_postal_code("InvalidCity")
    assert result == []

# -----------------------
# Tests for DataFrame-dependent functions
# -----------------------
def test_add_cities():
    data = {"ville": ["Paris", "Lyon", "InvalidCity", None]}
    df = pd.DataFrame(data)
    mock_obj = MockDataFrameClass(df)

    # Mock `get_postal_code`
    with patch("cleaner._transform.get_postal_code", side_effect=[["75001"], ["69000"], [], ["00000"]]):
        add_cities(mock_obj)
    
    expected_cp = [['75001'], ['69001'], [], ['00000']]
    assert mock_obj.df["cp"].tolist() == expected_cp


def test_change_domaine():
    data = {"nom_formation": ["Master Informatique Parcours IA", "Licence Math Parcours Analyse"]}
    df = pd.DataFrame(data)
    mock_obj = MockDataFrameClass(df)

    change_domaine(mock_obj)

    expected_domaine = [" Informatique ", " Math "]
    assert mock_obj.df["domaine"].tolist() == expected_domaine


def test_add_spe():
    data = {"nom_formation": ["Master Informatique Parcours IA", "Licence Math spécialité Analyse"]}
    df = pd.DataFrame(data)
    mock_obj = MockDataFrameClass(df)

    add_spe(mock_obj)

    expected_spe = [" IA", " Analyse"]
    assert mock_obj.df["spécialisation"].tolist() == expected_spe


def test_add_level():
    data = {"nom_formation": ["Master 2 Informatique", "Licence 3 Math"]}
    df = pd.DataFrame(data)
    mock_obj = MockDataFrameClass(df)

    add_level(mock_obj)

    expected_level = ["Master 2", "Licence 3"]
    assert mock_obj.df["niveau"].tolist() == expected_level


def test_add_id():
    data = {"nom_formation": ["Master Informatique"], "mail": ["test@example.com"]}
    df = pd.DataFrame(data)
    mock_obj = MockDataFrameClass(df)

    add_id(mock_obj)

    expected_id = [md5("Master Informatiquetest@example.com".encode()).hexdigest()]
    assert mock_obj.df["id"].tolist() == expected_id


def test_transform_data():
    data = {"nom_formation": ["Master Informatique Parcours IA"], "mail": ["test@example.com"], "ville": ["Paris"]}
    df = pd.DataFrame(data)
    mock_obj = MockDataFrameClass(df)

    with patch("cleaner._transform.get_postal_code", return_value=["75001"]):
        transform_data(mock_obj, actions=["add_cities", "add_spe", "change_domaine", "add_level", "add_id"])

    assert "cp" in mock_obj.df.columns
    assert "spécialisation" in mock_obj.df.columns
    assert "domaine" in mock_obj.df.columns
    assert "niveau" in mock_obj.df.columns
    assert "id" in mock_obj.df.columns
