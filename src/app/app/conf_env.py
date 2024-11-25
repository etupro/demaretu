import os
import logging

from utils.logging import setup_logger
setup_logger()

logger = logging.getLogger(__name__)

if not "EDU_DB_USER" in os.environ:
    from dotenv import load_dotenv
    if load_dotenv('./src/app/.env'):
        logger.info("Add credential")
    else:
        logger.error("Credential no load")
