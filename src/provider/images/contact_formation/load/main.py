from utils.conf_env import data_path, date
from sender import SenderVectorDB
import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def main():
    logger.info("Get processed data")
    docs_paths = list(data_path.glob("processed/**/*.parquet"))
    schema = "%Y/%m/%d"

    if len(docs_paths) == 0:
        logger.error("No data found")
        raise FileNotFoundError("Error: No processed data in directory")

    processed_data_path = os.path.join(data_path, "processed",
                                       date.strftime(schema),  'formations.parquet')
    df = pd.read_parquet(processed_data_path)
    logger.error("Init database vector")
    sender = SenderVectorDB(
            index_col="id",
            env_name_index="INDEX_FORMATION",
            other_cols=[
                "nom_formation", "domaine_formation",
                "niveau_formation", "presentation_formation", "contenu_formation",
                "url_fiche_formation", "mail_responsables", "universite",
                "ville", "url"
            ]
    )

    logger.error("Extract vector")
    df = sender.add_vector(
        df=df, col="nom_formation"
    )

    sender.send_data(df=df)


if __name__ == "__main__":
    logger.info("Début de injestion des données par la db")
    main()
    logger.info("Fin de injestion des données par la db")
