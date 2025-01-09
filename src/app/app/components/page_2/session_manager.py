import logging
import os
from pandas import DataFrame

# Logger configuration
logger = logging.getLogger(__name__)


class ManagerPage2:
    """
    Manages session data and operations for a matchmaking application.

    Attributes:
        col_formation_db (list): Columns for the formation database.
        col_post_db (list): Columns for the post database.
        match_phase (bool): Indicates whether the application is in the matching phase.
        data_storage (dict): Stores session data for posts and their associated formations.
        all_mail_content (dict): Stores email content for each responsible person.
        data_post (DataFrame): The DataFrame containing the post data.
    """

    col_formation_db = [
        "nom_formation",  "niveau", "domaine", "spécialisation",
        "mail_responsables", "mails", "universite",
        "cp", "url"
    ]
    col_post_db = [
        'id', 'content', 'title',
        'updated_at', 'number_departement',
        'tasks', 'status'
    ]

    def __init__(self, data_post: DataFrame, col_post_db: list = None, col_formation_db: list = None) -> None:
        """
        Initializes the SessionManager with provided data and optional column configurations.

        Args:
            data_post (DataFrame): DataFrame containing post data.
            col_post_db (list, optional): List of columns for the post database.
            col_formation_db (list, optional): List of columns for the formation database.
        """
        if col_formation_db is not None:
            self.col_formation_db = col_formation_db
        if col_post_db is not None:
            self.col_post_db = col_post_db

        self.match_phase = True
        self.data_storage = {}
        self.all_mail_content = {}
        self.data_post = data_post

    from components.page_2.reverse_func import get_postal_code, reverse_proposal
    get_postal_code = staticmethod(get_postal_code)

    def all_post_have_formations(self) -> bool:
        """
        Checks if all posts in the storage have associated formations.

        Returns:
            bool: True if all posts have formations, False otherwise.
        """
        logger.debug(f"Number of data stored: {len(self.get_data().keys())}")
        return all(
            len(post_tasks["proposal"]) > 0
            for post_tasks in self.data_storage.values()
        )

    def change_phase(self):
        """
        Switches the application phase from matching to the next step.
        Updates the session state to signal the matching phase is completed.
        """
        logger.debug("Changed match_phase")
        self.match_phase = not self.match_phase

    def is_matching_step(self) -> bool:
        """
        Determines whether the application is in the matching step.

        Returns:
            bool: True if matching step conditions are met, False otherwise.
        """
        return (self.data_storage != {} and
                not self.all_post_have_formations()) or self.match_phase

    def exist_idx_in_storage(self, idx: int) -> bool:
        """
        Checks if an index exists in the data storage.

        Args:
            idx (int): The index to check.

        Returns:
            bool: True if the index does not exist, False otherwise.
        """
        return idx not in self.data_storage

    # Getter methods
    def get_post_data(self, idx: int) -> dict:
        """
        Retrieves data for a specific post by its index.

        Args:
            idx (int): Index of the post.

        Returns:
            dict: Data for the specified post.
        """
        return self.data_storage[idx]

    def get_data(self) -> bool:
        """
        Retrieves all session data.

        Returns:
            dict: Dictionary of all session data.
        """
        return self.data_storage

    def get_post_in_dictionnary(self):
        """
        Converts the DataFrame of posts into a dictionary.

        Returns:
            list: List of dictionaries representing posts.
        """
        return self.data_post.to_dict(orient="records")

    def get_recommandation_formation_from_in_vectorial_db(self, post: dict, formations_db) -> DataFrame:
        """
        Retrieves recommended formations for a given post from the vectorial database.

        Args:
            post (dict): Data of the post for which recommendations are needed.
            formations_db: The formations database object.

        Returns:
            DataFrame: DataFrame containing the recommended formations.
        """
        if not isinstance(post["number_departement"], type(None)):
            search_case = [
                {"prefix": {"cp": {"value": post["number_departement"]}}},
                {"knn": {
                    "vector_index": {
                        "vector": post["vector_index"],
                        "k": 350
                    }
                }}
            ]
        else:
            search_case = [
                {"knn": {
                    "vector_index": {
                        "vector": post["vector_index"],
                        "k": 350
                    }
                }}
            ]
            title=post["title"]
            logger.warning(f"No departement found for post: {title}")
        return formations_db.get_data(
            settings_index={
                "size": 100,
                "_source": self.col_formation_db,
                "query": {
                    "bool": {
                        "must": search_case
                    }
                }
            }
        )

    def get_templates_mail(self):
        """
        Reads and retrieves the email template.

        Returns:
            tuple: A string with the email template and a boolean indicating if an error occurred.
        """
        try:
            TEMPLATE_MAIL_PATH = os.environ["PATH_FILE_TEMPLATE"]
            with open(TEMPLATE_MAIL_PATH, mode="r") as f:
                return f.read(), False
        except FileNotFoundError:
            logger.error(f"Email template not found: {TEMPLATE_MAIL_PATH}")
            return "", True

    def get_df_recommanded_of_post(self, idx: int) -> DataFrame:
        """
        Retrieves the recommended formations for a specific post as a DataFrame.

        Args:
            idx (int): Index of the post.

        Returns:
            DataFrame: DataFrame of recommended formations.
        """
        return self.data_storage[idx]["df"]

    # Adder methods
    def add_post_to_storage(self, post: dict, idx: int, proposal: DataFrame):
        """
        Adds a post to the data storage.

        Args:
            post (dict): The post data.
            idx (int): Index of the post.
            proposal (DataFrame): Recommended formations for the post.
        """
        self.data_storage[idx] = {
            "title": post["title"],
            "number_departement": post["number_departement"],
            "tasks": post["tasks"],
            "proposal": [],
            "df": proposal
        }

    def add_selected_formations_to_post(self, idx: int, name_formations: list):
        """
        Adds selected formations to a specific post.

        Args:
            idx (int): Index of the post.
            name_formations (list): List of selected formation names.
        """
        self.data_storage[idx]["proposal"] = name_formations

    def add_mail_content(self, content: str, dico: dict, responsable: str):
        """
        Adds content for an email to the storage.

        Args:
            content (str): The email content.
            dico (dict): Dictionary containing recipient details.
            responsable (str): Name of the responsible person.
        """
        self.all_mail_content[responsable] = {
            "responsible_name": responsable,
            "mail": dico["detail"]["mail"],
            "content": content,
            "statut": "A envoyer"
        }

    # Sender method
    def sent_to_google_sheet(self, drive_client) -> bool:
        """
        Sends the email data to a Google Sheet.

        Args:
            drive_client: Drive client for interacting with Google Sheets.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        df = DataFrame(list(self.all_mail_content.values()))
        try:
            gs = drive_client.get_sheet(
                name=os.environ['NAME_SHEET_FORMATION'],
                id_folder=os.environ['ID_FOLDER_DEMAREDU']
            )
            sh1 = gs.sheet1
            file = sh1.get_values() + df.to_numpy().tolist()
            sh1.update(file, 'A2')
            return True
        except Exception as e:
            logger.error(f"Error writing to Google Sheets: {e}")
            return False
