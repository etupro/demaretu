import conftest
import pytest
import pandas as pd
from cleaner import CleanerFormation


@pytest.fixture
def sample_dataframe():
    """Fixture pour un DataFrame d'exemple."""
    data = {
        "mail_responsables": ['{"John":"john@example.com", "Jane":"jane@example.com"}'],
        "presentation_formation": ["Introduction <!-- HTML Comment --> to Python"],
        "contenu_formation": ["Content <!-- Hidden --> of the course"],
        "nom_formation": ["DataScienceCourse"],
        "niveau_formation": ["master"],
    }
    return pd.DataFrame(data)


def test_format_colomns(sample_dataframe):
    cf = CleanerFormation(sample_dataframe.copy())
    cf.format_colomns()

    assert isinstance(cf.df.mail_responsables.iloc[0], dict)
    assert "John" in cf.df.mail_responsables.iloc[0]


def test_clean_desc_str(sample_dataframe):
    cf = CleanerFormation(sample_dataframe.copy())
    cf.format_colomns()
    cf.clean_desc_str()

    assert "<!--" not in cf.df.presentation_formation.iloc[0]
    assert "<!--" not in cf.df.contenu_formation.iloc[0]

    assert cf.df.nom_formation.iloc[0] == "Data Science Course"


def test_filter_data(sample_dataframe):
    sample_dataframe["niveau_formation"] = ["doctorat"]
    sample_dataframe["nom_formation"] = ["ModuleIntro"]
    cf = CleanerFormation(sample_dataframe.copy())
    cf.filter_data()

    assert cf.df.empty


def test_explode_by_responsable(sample_dataframe):
    cf = CleanerFormation(sample_dataframe.copy())
    cf.format_colomns()
    cf.clean_desc_str()
    cf.explode_by_responsable()

    assert len(cf.df) == 2
    assert cf.df.iloc[0].mails == "john@example.com"
    assert cf.df.iloc[1].mails == "jane@example.com"


def test_full_pipeline(sample_dataframe):
    cf = CleanerFormation(sample_dataframe.copy())
    result = cf()

    assert not result.empty
    assert "<!--" not in result.presentation_formation.iloc[0]
    assert result.nom_formation.iloc[0] == "Data Science Course"
    assert len(result) == 2
