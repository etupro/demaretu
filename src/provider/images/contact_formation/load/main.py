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

    processed_data_path = os.path.join(
        data_path, "processed",
        date.strftime(schema),  'formations.parquet'
    )
    df = pd.read_parquet(processed_data_path)
    logger.info("Init database vector")
    sender = SenderVectorDB(
            index_col="id",
            env_name_index="INDEX_FORMATION",
            other_cols=df.columns.to_list()
    )
    logger.info("Extract vector")
    df = sender.add_vector(
        df=df, col="domaine"
    )

    sender.send_data(df=df)


if __name__ == "__main__":
    logger.info("Début de injestion des données par la db")
    main()
    logger.info("Fin de injestion des données par la db")
