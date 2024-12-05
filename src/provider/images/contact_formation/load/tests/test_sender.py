import pytest
import conf_test
from unittest.mock import patch
from sentence_transformers import SentenceTransformer
import pandas as pd
from utils.sender import SenderVectorDB


@pytest.fixture
def mock_environment_variables(monkeypatch):
    """Fixture to set up environment variables."""
    monkeypatch.setenv("OPTION_DB_VECTOR", "{'http_compress': True}")
    monkeypatch.setenv("HOST_DB_VECTOR", "[{'host': 'localhost', 'port': 9200}]")
    monkeypatch.setenv("TEST_INDEX", "test_index")


@pytest.fixture
def vector_db(mock_environment_variables):
    """Fixture to initialize a SenderVectorDB instance."""
    return SenderVectorDB(env_name_index="TEST_INDEX")


def test_initialization(vector_db):
    """Test class initialization with environment variables."""
    assert vector_db.index_name_db == "test_index"
    assert isinstance(vector_db.model, SentenceTransformer)


def test_add_vector(vector_db):
    """Test the add_vector method for embedding text."""
    data = {"text_column": ["sample text"]}
    df = pd.DataFrame(data)
    result_df = vector_db.add_vector(df, "text_column")
    assert "vector_index" in result_df.columns
    assert len(result_df["vector_index"][0]) == vector_db.vector_dim


@patch("opensearchpy.OpenSearch")
def test_get_all_id_data(mock_opensearch, vector_db):
    """Test retrieval of all IDs from the OpenSearch index."""
    mock_response = {
        "hits": {
            "hits": [{"_source": {"id": "123"}}, {"_source": {"id": "456"}}]
        }
    }
    mock_opensearch.return_value.search.return_value = mock_response
    vector_db.db = mock_opensearch()
    ids = vector_db.get_all_id_data()
    assert ids == ["123", "456"]


@patch("opensearchpy.OpenSearch")
def test_get_data(mock_opensearch, vector_db):
    """Test retrieval of data from the OpenSearch index."""
    mock_response = {
        "hits": {
            "hits": [
                {"_source": {"id": "123", "nom_formation": "Test"}},
                {"_source": {"id": "456", "nom_formation": "Another Test"}}
            ]
        }
    }
    mock_opensearch.return_value.search.return_value = mock_response
    vector_db.db = mock_opensearch()
    df = vector_db.get_data(cols=["id", "nom_formation"])
    assert len(df) == 2
    assert "nom_formation" in df.columns


@patch("opensearchpy.OpenSearch")
def test_create_index(mock_opensearch, vector_db):
    """Test creation of an OpenSearch index with proper settings."""
    mock_opensearch.return_value.indices.exists.return_value = False
    vector_db.db = mock_opensearch()
    vector_db.vector_dim = 768
    vector_db.create_index()
    mock_opensearch.return_value.indices.create.assert_called_once()

@patch("opensearchpy.OpenSearch")
def test_send_data(mock_opensearch, vector_db):
    """Test sending data to the OpenSearch index."""
    mock_opensearch.return_value.indices.exists.return_value = True
    mock_opensearch.return_value.search.return_value = {"hits": {"hits": []}}
    vector_db.db = mock_opensearch()
    vector_db.other_cols = ["nom_formation"]

    data = {
        "id": ["1", "2"],
        "vector_index": [[0.1] * 768, [0.2] * 768],
        "nom_formation": ["Test 1", "Test 2"]
    }
    df = pd.DataFrame(data)
    vector_db.send_data(df)
    assert mock_opensearch.return_value.index.call_count == 2
