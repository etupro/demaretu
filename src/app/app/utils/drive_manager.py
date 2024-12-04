from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import gspread
import logging
import os

logger = logging.getLogger(__name__)


class DriveManager:
    """
    A class to manage interactions with Google Drive and Google Sheets 
    using PyDrive2 and gspread libraries.

    Attributes:
        drive (GoogleDrive): An authenticated instance of GoogleDrive.
        gc (gspread.Client): An authenticated instance of gspread for Google Sheets interaction.
    """

    def __init__(self):
        """
        Initializes the DriveManager class by authenticating with Google APIs.
        
        The credentials file path must be specified in the `PATH_CRED_DRIVE` 
        environment variable.
        
        Raises:
            KeyError: If the `PATH_CRED_DRIVE` environment variable is not set.
            Exception: If authentication fails.
        """
        try:
            credentials_path = os.environ["PATH_CRED_DRIVE"]
        except KeyError as e:
            logger.error("The environment variable 'PATH_CRED_DRIVE' is not set.")
            raise KeyError("The 'PATH_CRED_DRIVE' environment variable is required but not set.") from e

        try:
            gauth = GoogleAuth()
            gauth.settings["client_config_file"] = credentials_path
            gauth.LocalWebserverAuth()
            self.drive = GoogleDrive(gauth)
            
            self.gc = gspread.authorize(gauth.credentials)
            logger.info("Successfully authenticated with Google APIs.")
        except Exception as e:
            logger.error("Failed to authenticate with Google APIs.", exc_info=True)
            raise Exception("Authentication with Google APIs failed.") from e

    def get_sheet(self, name: str, id_folder: str = None):
        """
        Opens a Google Sheet by its name.

        Args:
            name (str): The name of the Google Sheet to open.

        Returns:
            gspread.models.Spreadsheet: A Google Sheet instance.

        Raises:
            gspread.exceptions.SpreadsheetNotFound: If the sheet with the given name is not found.
        """
        try:
            logger.info(f"Attempting to open Google Sheet: {name}")
            if id_folder:
                return self.gc.open(title=name, folder_id=id_folder)
            else:
                return self.gc.open(title=name)
        except Exception:
            logger.error(f"Failed to open Google Sheet '{name}'.", exc_info=True)
            raise

    def get_drive(self) -> GoogleDrive:
        """
        Returns the authenticated GoogleDrive instance.

        Returns:
            GoogleDrive: An authenticated GoogleDrive object.
        """
        logger.info("Returning authenticated GoogleDrive instance.")
        return self.drive
