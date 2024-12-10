import pytest
import pandas as pd
from cleaner._clean import clean_desc_str, format_columns, clean_data

# Mock logger to avoid real logging during tests
from cleaner._clean import logger
logger.disabled = True

# Mock class to simulate the `self` object with a DataFrame
class MockDataFrameClass:
    def __init__(self, df):
        self.df = df
    from cleaner._clean import clean_desc_str, format_columns, clean_data

# -------------------------
# Tests for format_columns
# -------------------------
def test_format_columns():
    # Data with stringified dictionaries
    data = {
        "mail_responsables": ["{'resp1': 'email1@example.com', 'resp2': 'email2@example.com'}"]
    }
    df = pd.DataFrame(data)
    mock_obj = MockDataFrameClass(df)

    # Call the function
    format_columns(mock_obj)

    # Expected output
    expected = [{"resp1": "email1@example.com", "resp2": "email2@example.com"}]
    assert mock_obj.df["mail_responsables"].tolist() == expected

# -------------------------
# Tests for clean_desc_str
# -------------------------
def test_clean_desc_str():
    # Data for testing
    data = {
        "presentation_formation": [
            "Welcome <!--HTML comment--> to the course", "Welcome  to the course"
        ],
        "contenu_formation": ["Content  here", "Content <!--Another comment--> here"],
        "nom_formation": ["MasterInformatique", "LicenceMathematiques"],
        "mail_responsables": [
            {"resp1": "email1@example.com", "resp2": "email2@example.com"},
            {"resp1": "email1@example.com"}
        ]
    }
    df = pd.DataFrame(data)
    print(df)
    mock_obj = MockDataFrameClass(df)

    # Call the function
    clean_desc_str(mock_obj)

    # Expected results
    expected_presentation = ["Welcome  to the course", "Welcome  to the course"]
    expected_contenu = ["Content  here", "Content  here"]
    expected_nom = ["Master Informatique", "Licence Mathematiques"]
    expected_mails = [["email1@example.com", "email2@example.com"], ["email1@example.com"]]

    assert mock_obj.df["presentation_formation"].tolist() == expected_presentation
    assert mock_obj.df["contenu_formation"].tolist() == expected_contenu
    assert mock_obj.df["nom_formation"].tolist() == expected_nom
    assert mock_obj.df["mails"].tolist() == expected_mails

# -------------------------
# Tests for clean_data
# -------------------------
def test_clean_data():
    # Data for testing
    data = {
        "presentation_formation": ["Welcome <!--HTML comment--> to the course"],
        "contenu_formation": ["Content <!--Another comment--> here"],
        "nom_formation": ["MasterInformatique"],
        "mail_responsables": ["{'resp1': 'email1@example.com', 'resp2': 'email2@example.com'}"]
    }
    df = pd.DataFrame(data)
    mock_obj = MockDataFrameClass(df)

    # Call the function
    clean_data(mock_obj, actions=["clean_desc_str"])

    # Expected results
    expected_presentation = ["Welcome  to the course"]
    expected_contenu = ["Content  here"]
    expected_nom = ["Master Informatique"]
    expected_mails = [["email1@example.com", "email2@example.com"]]

    assert mock_obj.df["presentation_formation"].tolist() == expected_presentation
    assert mock_obj.df["contenu_formation"].tolist() == expected_contenu
    assert mock_obj.df["nom_formation"].tolist() == expected_nom
    assert mock_obj.df["mails"].tolist() == expected_mails
