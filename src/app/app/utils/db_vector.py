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
            raise

    def get_db(self):
        try:
            return self.client
        except Exception:
            logger.error(traceback.format_exc())
            raise
