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

if "MAMBA_EXE" in os.environ:
    date = datetime.now()
    data_path = Path("data")
else:
    date = datetime.strptime(os.environ["DATE_FOLDER"], '%Y-%m-%d')
    data_path = Path("/app/data/to_ingest")
