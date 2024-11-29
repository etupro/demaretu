from pathlib import Path
from datetime import datetime
import os
import logging


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filemode='w'
    )

setup_logger()

logger = logging.getLogger(__name__)
os.environ

if "DATE_FOLDER" in os.environ:
    date_str = os.environ["DATE_FOLDER"]
    date = datetime.strptime(date_str, '%Y-%m-%d')
    data_path = Path("/app/data/to_ingest")
    logger.info(f"Run in container for date: {date_str}")
else:
    import dotenv
    dotenv.load_dotenv()
    date = datetime.now()
    data_path = Path("./data")
    logger.info("Run in local")
