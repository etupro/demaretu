import conf_test
import pytest
from utils.drive_manager import DriveManager
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_drive_manager_environment():
    """
    Pytest fixture to mock the environment and dependencies required by DriveManager.
    
    Mocks:
        - The PATH_CRED_DRIVE environment variable.
        - GoogleAuth for authentication.
        - GoogleDrive for drive interactions.
        - gspread.authorize for Google Sheets interactions.

    Returns:
        tuple: (MockGoogleAuth, MockGoogleDrive, mock_authorize)
    """
    with patch.dict("os.environ", {"PATH_CRED_DRIVE": "/path/to/mock/credentials.json"}), \
         patch("utils.drive_manager.GoogleAuth") as MockGoogleAuth, \
         patch("utils.drive_manager.GoogleDrive") as MockGoogleDrive, \
         patch("utils.drive_manager.gspread.authorize") as mock_authorize:

        # Set up mock objects for GoogleAuth, GoogleDrive, and gspread.authorize
        mock_auth = MagicMock()
        MockGoogleAuth.return_value = mock_auth
        mock_drive = MagicMock()
        MockGoogleDrive.return_value = mock_drive
        mock_client = MagicMock()
        mock_authorize.return_value = mock_client

        yield MockGoogleAuth, MockGoogleDrive, mock_authorize


def test_drive_manager_initialization_success(mock_drive_manager_environment):
    """
    Test that DriveManager initializes successfully when the environment variable is set 
    and authentication succeeds.
    """
    MockGoogleAuth, MockGoogleDrive, mock_authorize = mock_drive_manager_environment

    manager = DriveManager()

    # Assert initialization creates proper attributes
    assert manager.drive is not None
    assert manager.gc is not None
    MockGoogleAuth.assert_called_once()
    mock_authorize.assert_called_once_with(MockGoogleAuth.return_value.credentials)


def test_drive_manager_missing_env_variable():
    """
    Test that DriveManager raises a KeyError if the PATH_CRED_DRIVE environment variable is not set.
    """
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(KeyError, match="The 'PATH_CRED_DRIVE' environment variable is required but not set."):
            DriveManager()


def test_drive_manager_authentication_failure(mock_drive_manager_environment):
    """
    Test that DriveManager raises an exception if authentication fails.
    """
    MockGoogleAuth, MockGoogleDrive, mock_authorize = mock_drive_manager_environment
    MockGoogleAuth.side_effect = Exception("Mock authentication failed")

    with pytest.raises(Exception, match="Authentication with Google APIs failed."):
        DriveManager()


def test_get_sheet_success(mock_drive_manager_environment):
    """
    Test that get_sheet successfully opens a Google Sheet by name.
    """
    _, _, mock_authorize = mock_drive_manager_environment

    # Mock the behavior of opening a sheet
    mock_sheet = MagicMock()
    mock_authorize.return_value.open.return_value = mock_sheet

    manager = DriveManager()
    sheet = manager.get_sheet("Test Sheet")

    assert sheet == mock_sheet
    mock_authorize.return_value.open.assert_called_once_with("Test Sheet")


def test_get_sheet_failure(mock_drive_manager_environment):
    """
    Test that get_sheet raises an exception if the sheet cannot be opened.
    """
    _, _, mock_authorize = mock_drive_manager_environment

    # Mock failure in opening the sheet
    mock_authorize.return_value.open.side_effect = Exception("Sheet not found")

    manager = DriveManager()
    with pytest.raises(Exception, match="Sheet not found"):
        manager.get_sheet("Nonexistent Sheet")


def test_get_drive(mock_drive_manager_environment):
    """
    Test that get_drive returns the authenticated GoogleDrive instance.
    """
    _, MockGoogleDrive, _ = mock_drive_manager_environment

    manager = DriveManager()
    drive = manager.get_drive()

    assert drive == MockGoogleDrive.return_value
