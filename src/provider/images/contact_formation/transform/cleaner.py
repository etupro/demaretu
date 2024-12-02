import pandas as pd
import re
import logging

logger = logging.getLogger(__name__)


class CleanerFormation:
    """
    A class to clean and transform a DataFrame containing training program data.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the CleanerFormation object with a DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame to be cleaned and transformed.
        """
        self.df = df

    def format_colomns(self):
        """
        Convert the 'mail_responsables' column from stringified dictionaries to actual dictionaries.
        This uses the `eval` function to interpret the string content.
        """
        self.df.mail_responsables = self.df.mail_responsables.map(eval)
        logger.info("Format data done !")

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

    def filter_data(self):
        """
        Filter the DataFrame by:
        1. Excluding rows where 'niveau_formation' is "doctorat".
        2. Excluding rows where 'nom_formation' contains the word "Module".
        """
        self.df = self.df[self.df.niveau_formation != "doctorat"]
        self.df = self.df[~self.df.nom_formation.str.contains("Module")]
        logger.info("Filter data done !")

    def explode_by_responsable(self):
        """
        Expand rows to create one row per 'mail_responsables' and 'mails' entry.
        This ensures that each email is associated with its own row in the DataFrame.
        """
        self.df = self.df.explode(["mail_responsables", "mails"])
        self.df = self.df[(~self.df.mails.isna())]
        logger.info("Explode data done !")

    def __call__(self, *args, **kwds) -> pd.DataFrame:
        """
        Execute the entire data cleaning pipeline in sequence:
        1. Filter the data.
        2. Format columns.
        3. Clean specific string fields.
        4. Explode the data by 'responsable'.

        Returns:
            pd.DataFrame: The cleaned and transformed DataFrame.
        """
        self.filter_data()
        self.format_colomns()
        self.clean_desc_str()
        self.explode_by_responsable()
        return self.df


if __name__ == '__main__':
    cf_module = CleanerFormation(pd.read_csv("formations.csv"))
    df_clean = cf_module()
    df_clean.to_parquet("clean_csv.parquet", index=False)
