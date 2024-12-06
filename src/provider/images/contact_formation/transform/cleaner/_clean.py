import re
import logging

logger = logging.getLogger(__name__)

def clean_desc_str(self):
    """
    Perform cleaning of specific text fields:
    1. Remove HTML comments from 'presentation_formation' and 'contenu_formation' columns.
    2. Split camel case in the 'nom_formation' column to make it more readable.
    3. Extract email addresses from the 'mail_responsables' dictionaries into a new 'mails' column.
    """
    pattern = r"<!--(.*?)-->"

    remove_html_comment_col_list = [
        "presentation_formation", "contenu_formation"
    ]

    for col in remove_html_comment_col_list:
        self.df[col] = self.df[col].map(
            lambda x: re.sub(pattern, "", str(x), flags=re.DOTALL)
        )

    self.df.nom_formation = self.df.nom_formation.map(
        lambda x: " ".join(re.split(r'(?<=[a-z])(?=[A-Z])', x))
    )

    self.df["mails"] = self.df.mail_responsables.map(
        lambda x: list(x.values())
    )
    logger.info("Clean data done !")

def format_columns(self):
    """
    Convert the 'mail_responsables' column from stringified dictionaries to actual dictionaries.
    This uses the `eval` function to interpret the string content.
    """
    self.df.mail_responsables = self.df.mail_responsables.map(eval)
    logger.debug("Format data done !")

def clean_data(self, actions:list):
    self.format_columns()
    if "clean_desc_str" in actions:
        self.clean_desc_str()