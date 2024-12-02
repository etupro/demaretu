import conftest
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from sender import SenderVectorDB


@pytest.fixture
def mock_opensearch():
    """Mock pour OpenSearch."""
    with patch('sender.OpenSearch') as mock:
        yield mock


@pytest.fixture
def mock_sentence_transformer():
    """Mock pour SentenceTransformer."""
    with patch('sender.SentenceTransformer') as mock:
        mock_instance = MagicMock()
        mock_instance.encode.return_value = [0.1] * 768
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock pour les variables d'environnement."""
    monkeypatch.setenv("INDEX_FORMATION", "test_index")
    monkeypatch.setenv("OPTION_DB_VECTOR", "{'http_auth': ('user', 'pass')}")
    monkeypatch.setenv(
        "HOST_DB_VECTOR", "[{'host': 'localhost', 'port': 9200}]")


@pytest.fixture
def sample_dataframe():
    """Un DataFrame d'exemple."""
    data = {
        "id": [1, 2],
        "nom_formation": ["Formation A", "Formation B"],
        "domaine_formation": ["Domaine A", "Domaine B"],
        "presentation_formation": ["Présentation A", "Présentation B"],
    }
    return pd.DataFrame(data)


def test_initialization(mock_opensearch, mock_env_vars):
    """Tester l'initialisation de SenderVectorDB."""
    db_instance = SenderVectorDB()
    assert db_instance.index_name_db == "test_index"
    mock_opensearch.assert_called_once()


def test_add_vector(mock_sentence_transformer, sample_dataframe, mock_env_vars):
    """Tester la méthode add_vector."""
    db_instance = SenderVectorDB()
    df = db_instance.add_vector(sample_dataframe, "presentation_formation")
    assert "vector_index" in df.columns
    assert len(df["vector_index"][0]) == 768


def test_create_index(mock_opensearch, mock_env_vars):
    """Tester la méthode create_index."""
    mock_db = mock_opensearch.return_value
    mock_db.indices.exists.return_value = False

    db_instance = SenderVectorDB()
    db_instance.create_index()

    mock_db.indices.create.assert_called_once()
    args, kwargs = mock_db.indices.create.call_args
    assert kwargs["index"] == "test_index"
    assert "mappings" in kwargs["body"]


def test_send_data(mock_opensearch, mock_sentence_transformer, mock_env_vars, sample_dataframe):
    """Tester la méthode send_data."""
    mock_db = mock_opensearch.return_value
    mock_db.indices.exists.return_value = False

    db_instance = SenderVectorDB(
        other_cols=[
            "nom_formation", "domaine_formation", "presentation_formation"
        ])
    db_instance.add_vector(sample_dataframe, "presentation_formation")
    db_instance.send_data(sample_dataframe)

    assert mock_db.index.call_count == len(sample_dataframe)
    for i, call in enumerate(mock_db.index.call_args_list):
        args, kwargs = call
        assert kwargs["index"] == "test_index"
        assert kwargs["id"] == sample_dataframe.iloc[i]["id"]
