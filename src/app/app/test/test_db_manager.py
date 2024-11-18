import conf_test
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError
from utils.db_manager import DBManager


def test_db_manager_initialization_success():
    """Test that the DBManager is correctly initialized."""
    with patch("utils.db_manager.create_engine") as mock_create_engine:
        mock_create_engine.return_value = MagicMock()

        db_manager = DBManager(
            db_user="test_user",
            db_password="test_password",
            db_host="localhost",
            db_port="5432",
            db_database="test_db"
        )

        mock_create_engine.assert_called_once()
        assert db_manager.engine is not None
        assert db_manager.SessionLocal is not None


def test_db_manager_initialization_failure():
    """Test that the DBManager raises an exception in case of an initialization problem."""
    with patch("utils.db_manager.create_engine",
               side_effect=OperationalError("Connection failed", None, None)):
        with pytest.raises(OperationalError, match="Connection failed"):
            DBManager(
                db_user="test_user",
                db_password="test_password",
                db_host="localhost",
                db_port="5432",
                db_database="test_db"
            )
