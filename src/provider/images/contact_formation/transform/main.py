
from utils.conf_env import date, data_path
import os
import traceback
from cleaner import CleanerFormation
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def main(date):
    try:
        logger.info("Debut de la tâches")
        date = date.strftime("%Y/%m/%d")

        data_raw_path = os.path.join(
            data_path, "raw", date, "formations.csv")
        data_processed_path = os.path.join(
            data_path, "processed", date)

        # Get data:
        df_raw = pd.read_csv(data_raw_path)
        cf = CleanerFormation(df=df_raw)
        sub_cols = ['id', 'nom_formation', 'domaine', 'niveau',
                    "spécialisation", 'mail_responsables', 'mails',
                    'universite', "cp",  "url"]
        df_processed = cf(sub_cols)

        os.makedirs(data_processed_path, exist_ok=True)
        df_processed.to_parquet(os.path.join(
            data_processed_path, "formations.parquet"))

    except Exception:
        logger.error(traceback.format_exc())
    return 1


if __name__ == "__main__":
    main(date)
