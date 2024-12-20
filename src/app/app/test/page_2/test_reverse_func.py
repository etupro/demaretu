import conf_test_lvl_2
import pytest
from unittest.mock import patch, MagicMock
from components.page_2.reverse_func import get_postal_code, reverse_proposal
import pandas as pd


def test_get_postal_code_success():
    """
    Test successful retrieval of postal codes for a given city.
    """
    city = "Paris"
    mock_response_data = {
        "features": [
            {"properties": {"postcode": "75000"}}
        ]
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response_data
        
        postal_codes = get_postal_code(city)
        
        assert postal_codes == ["75"], "Postal code should match the first two digits"


def test_get_postal_code_multiple_cities():
    """
    Test successful retrieval of postal codes for multiple cities.
    """
    cities = "Paris,Lyon"
    mock_responses = [
        {"features": [{"properties": {"postcode": "75000"}}]},
        {"features": [{"properties": {"postcode": "69000"}}]}
    ]

    with patch("requests.get") as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=200, json=MagicMock(return_value=mock_responses[0])),
            MagicMock(status_code=200, json=MagicMock(return_value=mock_responses[1]))
        ]

        postal_codes = get_postal_code(cities)
        
        assert postal_codes == ["75", "69"], "Postal codes for multiple cities should match"


def test_get_postal_code_failure():
    """
    Test failure case for the postal code retrieval due to API error.
    """
    city = "NonExistentCity"

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 404

        with pytest.raises(Exception, match="HTTP Error: 404"):
            get_postal_code(city)


def test_reverse_proposal_success():
    """
    Test reverse_proposal function with valid input.
    """
    mock_formations_db = MagicMock()

    formations_data = pd.DataFrame({
        "nom_formation": ["Formation1", "Formation2"],
        "mail_responsables": ["responsable1@example.com", "responsable2@example.com"],
        "mails": ["mail1@example.com", "mail2@example.com"]
    })
    mock_formations_db.get_data.return_value = formations_data

    mock_self = MagicMock()
    mock_self.get_data.return_value = {
        1: {
            "proposal": ["Formation1"],
            "title": "Test Post",
            "number_departement": "75",
            "tasks": "Task1"
        }
    }
    mock_self.col_formation_db = ["nom_formation", "mail_responsables", "mails"]

    result = reverse_proposal(mock_self, mock_formations_db)

    assert isinstance(result, dict), "Result should be a dictionary"
    assert "responsable1@example.com" in result, "Responsable should be in the result"
    assert result["responsable1@example.com"]["tasks"][0]["title"] == "Test Post", "Post data should match"
    assert "Formation1" in result["responsable1@example.com"]["detail"]["formations"], "Formation1 should be included"


def test_reverse_proposal_empty_data():
    """
    Test reverse_proposal with empty formations or posts.
    """
    mock_formations_db = MagicMock()
    mock_formations_db.get_data.return_value = pd.DataFrame([])
    mock_self = MagicMock()
    mock_self.get_data.return_value = {}

    with pytest.raises(Exception, match="Formation or session data is missing or empty"):
        reverse_proposal(mock_self, mock_formations_db)
