import pandas as pd
import logging


logger = logging.getLogger(__name__)


class CleanerFormation:
    """
    A class to clean and transform a DataFrame containing training program data.
    """

    from ._filter import filter_data
    from ._transform import transform_data, add_cities, get_postal_code, compiler_degres_level,\
        change_domaine, add_level, add_spe, add_id
    from ._clean import clean_data, format_columns, clean_desc_str

    get_postal_code = staticmethod(get_postal_code)

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the CleanerFormation object with a DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame to be cleaned and transformed.
        """
        self.df = df

    def explode_by_responsable(self):
        """
        Expand rows to create one row per 'mail_responsables' and 'mails' entry.
        This ensures that each email is associated with its own row in the DataFrame.
        """
        self.df = self.df.explode(["mail_responsables", "mails"])
        self.df = self.df[(~self.df.mails.isna())]
        logger.info("Explode data done !")

    def __call__(self, subcols:list=None, *args, **kwds) -> pd.DataFrame:
        """
        Execute the entire data cleaning pipeline in sequence:
        1. Filter the data.
        2. Format columns.
        3. Clean specific string fields.
        4. Explode the data by 'responsable'.

        Returns:
            pd.DataFrame: The cleaned and transformed DataFrame.
        """
        self.clean_data(actions=["clean_desc_str"])
        self.transform_data(actions=["add_cities", "add_spe", "change_domaine", "add_level"])
        self.filter_data()
        self.explode_by_responsable()
        self.transform_data(actions=["add_id"])
        if not isinstance(subcols, list):
            return self.df
        else:
            return self.df[subcols]


if __name__ == '__main__':
    cf_module = CleanerFormation(pd.read_csv("formations.csv"))
    df_clean = cf_module()
    df_clean.to_parquet("clean_csv.parquet", index=False)
