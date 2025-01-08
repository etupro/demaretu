import conf_test_lvl_2
import pytest
from unittest.mock import mock_open, MagicMock, patch
from pandas import DataFrame
from components.page_2.session_manager import ManagerPage2 as SessionManager


@pytest.fixture
def mock_data_post():
    return DataFrame({
        "id": [1, 2, 3],
        "content": ["Test content 1", "Test content 2", "Test content 3"],
        "title": ["Title 1", "Title 2", "Title 3"],
        "number_departement": ["75000", "69000", "13000"],
        "tasks": [[], [], []]
    })


@pytest.fixture
def session_manager(mock_data_post):
    return SessionManager(data_post=mock_data_post)


def test_initialization(session_manager, mock_data_post):
    assert session_manager.match_phase is True
    assert session_manager.data_storage == {}
    assert session_manager.all_mail_content == {}
    assert session_manager.data_post.equals(mock_data_post)


def test_add_post_to_storage(session_manager):
    post = {
        "title": "Test Title",
        "number_departement": "75000",
        "tasks": []
    }
    idx = 1
    proposal = DataFrame({"test": [1, 2, 3]})

    session_manager.add_post_to_storage(post, idx, proposal)

    assert idx in session_manager.data_storage
    assert session_manager.data_storage[idx]["title"] == "Test Title"
    assert session_manager.data_storage[idx]["number_departement"] == "75000"
    assert session_manager.data_storage[idx]["tasks"] == []
    assert session_manager.data_storage[idx]["df"].equals(proposal)


def test_get_post_data(session_manager):
    post = {
        "title": "Test Title",
        "number_departement": "75000",
        "tasks": []
    }
    idx = 1
    proposal = DataFrame({"test": [1, 2, 3]})

    session_manager.add_post_to_storage(post, idx, proposal)
    result = session_manager.get_post_data(idx)

    assert result["title"] == "Test Title"
    assert result["number_departement"] == "75000"
    assert result["tasks"] == []
    assert result["df"].equals(proposal)


def test_all_post_have_formations(session_manager):
    session_manager.data_storage = {
        1: {"proposal": ["Formation 1"]},
        2: {"proposal": ["Formation 2"]}
    }

    assert session_manager.all_post_have_formations() is True

    session_manager.data_storage[3] = {"proposal": []}
    assert session_manager.all_post_have_formations() is False


def test_change_phase(session_manager):
    assert session_manager.match_phase is True
    session_manager.change_phase()
    assert session_manager.match_phase is False
    session_manager.change_phase()
    assert session_manager.match_phase is True


def test_is_matching_step(session_manager):
    assert session_manager.is_matching_step() is True

    session_manager.match_phase = False
    session_manager.data_storage = {
        1: {"proposal": ["Formation 1"]},
        2: {"proposal": []}
    }
    assert session_manager.is_matching_step() is True

    session_manager.data_storage[2]["proposal"] = ["Formation 2"]
    assert session_manager.is_matching_step() is False


def test_get_templates_mail(session_manager):
    with patch("os.environ", {"PATH_FILE_TEMPLATE": "test_template.txt"}):
        with patch("builtins.open", mock_open(read_data="Template content")) as mock_file:
            content, error = session_manager.get_templates_mail()
            assert content == "Template content"
            assert error is False

    with patch("os.environ", {"PATH_FILE_TEMPLATE": "missing_template.txt"}):
        with patch("builtins.open", side_effect=FileNotFoundError):
            content, error = session_manager.get_templates_mail()
            assert content == ""
            assert error is True


def test_get_recommandation_formation_from_in_vectorial_db(session_manager):
    post = {
        "number_departement": "75000",
        "vector_index": [0.1, 0.2, 0.3]
    }

    mock_formations_db = MagicMock()
    mock_formations_db.get_data.return_value = DataFrame({
        "nom_formation": ["Formation 1", "Formation 2"],
        "niveau": ["Master", "Licence"],
        "domaine": ["Informatique", "Maths"]
    })

    result = session_manager.get_recommandation_formation_from_in_vectorial_db(post, mock_formations_db)

    mock_formations_db.get_data.assert_called_once()
    assert isinstance(result, DataFrame)
    assert "nom_formation" in result.columns