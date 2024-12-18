import logging
import os
import pandas as pd
from streamlit_utils.cache_ressource import get_vectorial_db, get_drive

# Logger configuration
logger = logging.getLogger(__name__)


class SessionManager:
    COL_DB = [
        "nom_formation",  "niveau", "domaine", "spécialisation",
        "mail_responsables", "mails", "universite",
        "cp", "url"
    ]

    def __init__(self) -> None:
        ## Var
        self.match_phase = True
        self.data_storage = {}
        self.all_mail_content = []
        
        ## Class
        self.posts_db = get_vectorial_db(
            env_name_index="INDEX_POST",
            index_col="id",
            other_cols=[
                'id', 'content', 'title',
                'updated_at', 'number_departement', 'tasks'
            ]
        )
        self.data_post = self.posts_db.get_data()
        self.formations_db = get_vectorial_db(
            index_col="id",
            env_name_index="INDEX_FORMATION",
            other_cols=SessionManager.COL_DB
        )
        self.drive_client = get_drive()

    from components.page_2.matchmaking_func import get_postal_code, reverse_proposal
    get_postal_code = staticmethod(get_postal_code)

    def all_post_have_formations(self):
        return all(
            len(post_tasks["proposal"]) > 0
            for post_tasks in self.get_data().values()
            )

    def change_phase(self):
        """
        Switches the application phase from matching to the next step.
        Updates the session state to signal the matching phase is completed.
        """
        self.match_phase = False
        logger.debug("Turned off: match_phase")

    def have_to_switch_step(self):
        return (
            any(len(post_tasks["proposal"]) == 0
                for post_tasks in self.data_storage.values()
                ) or
            not self.data_storage) and self.match_phase

    def get_post_data(self, idx: int):
        return self.data_storage[idx]

    def exist_idx_in_storage(self, idx: int):
        return idx not in self.data_storage

    def add_post_to_storage(self, post, idx, proposal):
        self.data_storage[idx] = {
            "title": post["title"],
            "number_departement": post["number_departement"],
            "tasks": post["tasks"],
            "proposal": [],
            "df": proposal
        }

    def add_selected_formation_to_post(self, idx: int, name_formations: list):
        self.data_storage[idx]["proposal"] = name_formations

    def get_data(self):
        return self.data_storage

    def get_post_in_dictionnary(self):
        return self.data_post.to_dict(orient="records")

    def get_recommandation_formation_from_in_vectorial_db(self, post):
        return self.formations_db.get_data(
            settings_index={
                "size": 100,
                "_source": self.COL_DB,
                "query":  {
                    "bool": {
                        "must": [
                            {"prefix": {"cp": {"value": post["number_departement"]}}},
                            {"knn": {
                                    "vector_index": {
                                        "vector": post["vector_index"],
                                        "k": 350
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        )

    def get_templates_mail(self):
        try:
            TEMPLATE_MAIL_PATH = os.environ["PATH_FILE_TEMPLATE"]
            with open(TEMPLATE_MAIL_PATH, mode="r") as f:
                return f.read(), True
        except FileNotFoundError:
            logger.error(f"Email template not found: {TEMPLATE_MAIL_PATH}")
            return "", False

    def sent_to_google_sheet(self):
        df = pd.DataFrame(self.all_mail_content)
        try:
            gs = self.drive_client.get_sheet(
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

    def add_mail_content(self, content, dico, responsable):
        self.all_mail_content.append({
            "responsible_name": responsable,
            "mail": dico["detail"]["mail"],
            "content": content,
            "statut": "A envoyer"
        })
        