import pytest
from unittest.mock import patch, MagicMock
from utils.db_vector import DBVector


def test_dbvector_initialization_success(mocker):
    """Test de l'initialisation réussie de DBVector."""
    mock_client = MagicMock()
    mock_opensearch = mocker.patch(
        "utils.db_vector.OpenSearch", return_value=mock_client)
    mock_logging_info = mocker.patch("utils.db_vector.logger.info")

    option_host = [{"host": "localhost", "port": 9200}]
    option_db = {"http_auth": ("user", "password")}

    db_vector = DBVector(option_host, option_db)

    mock_opensearch.assert_called_once_with(
        hosts=option_host, http_auth=("user", "password"))
    mock_logging_info.assert_called_once_with('DB initialized')
    assert db_vector.client == mock_client


def test_dbvector_initialization_failure(mocker:MagicMock):
    """Test de l'échec de l'initialisation de DBVector."""
    opensearch_mocker = mocker.patch("utils.db_vector.OpenSearch")
    opensearch_mocker.side_effect = Exception("Connection error")

    option_host = [{"host": "localhost", "port": 9200}]
    option_db = {"http_auth": ("user", "password")}
    with pytest.raises(Exception, match="Connection error"):
        db_vector = DBVector(option_host, option_db)
        assert db_vector.client is None


def test_get_db_success():
    """Test de la méthode get_db avec un client valide."""
    mock_client = MagicMock()
    db_vector = DBVector([], {})
    db_vector.client = mock_client

    client = db_vector.get_db()
    assert client == mock_client


def test_get_db_failure(mocker):
    """Test de la méthode get_db lorsque le client n'est pas initialisé."""
    db_vector = DBVector([], {})
    db_vector.client = None

    client = db_vector.get_db()
    assert client is None
