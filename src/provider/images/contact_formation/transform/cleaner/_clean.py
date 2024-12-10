import re
import logging

logger = logging.getLogger(__name__)


def clean_desc_str(self):
    """
    Perform cleaning of specific text fields in the DataFrame:
    1. Remove HTML comments from the 'presentation_formation' and 'contenu_formation' columns.
    2. Format the 'nom_formation' column by splitting camel case to improve readability.
    3. Extract email addresses from dictionaries in the 'mail_responsables' column 
       and store them in a new column called 'mails'.

    Effects:
        - Modifies the columns 'presentation_formation', 'contenu_formation', and 'nom_formation'.
        - Adds a new column 'mails' containing a list of email addresses extracted from 'mail_responsables'.
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
    
    This transformation assumes that the column contains stringified Python dictionaries.
    The `eval` function is used to parse these strings into actual dictionary objects.

    Effects:
        - Converts each value in the 'mail_responsables' column from a stringified dictionary 
          to a proper Python dictionary.

    Warning:
        - Using `eval` can be unsafe if the input data is not trusted. Make sure the source of 
          the DataFrame is secure before applying this function.
    """
    self.df.mail_responsables = self.df.mail_responsables.map(eval)
    logger.debug("Format data done !")


def clean_data(self, actions: list):
    """
    Perform a sequence of cleaning operations on the DataFrame based on the specified actions.

    Parameters:
        actions (list): A list of cleaning operations to apply. Supported actions:
            - "clean_desc_str": Calls the `clean_desc_str` method to clean textual fields.

    Effects:
        - Calls `format_columns` to convert the 'mail_responsables' column to dictionaries.
        - Conditionally applies additional cleaning actions based on the provided `actions` list.
    """
    self.format_columns()
    if "clean_desc_str" in actions:
        self.clean_desc_str()
