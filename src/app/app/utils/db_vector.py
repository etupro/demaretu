from opensearchpy import OpenSearch
import os
import logging
import traceback

logger = logging.getLogger(__name__)


class DBVector:
    def __init__(self, option_host: list, option_db: dict):
        try:
            self.client = OpenSearch(
                hosts=option_host,
                **option_db
            )
            logger.info('DB initialized')
        except Exception:
            logging.error(
                f"Error to initialized vectorial db: {traceback.format_exc()}")

    def get_db(self):
        try:
            return self.client
        except Exception:
            logger.error(traceback.format_exc())


try:
    option_db = eval(os.environ["OPTION_DB_VECTOR"])
    option_host = eval(os.environ["HOST_DB_VECTOR"])
    if isinstance(option_db, dict) and isinstance(option_host, list):
        DB_VECTORIAL = DBVector(
            option_db=option_db,
            option_host=option_host
        )
    else:
        raise ValueError(
            f"the type of option_db is {type(option_db)} and the type of option_host is {type(option_host)}")
except RuntimeError as e:
    logger.critical(f"Failed to initialize database managers: {e}")
    raise
