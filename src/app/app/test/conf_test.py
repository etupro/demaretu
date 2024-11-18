from pathlib import Path
import sys
from unittest.mock import patch
import os

path = Path(__file__).parent.parent
sys.path.append(str(path))

patch.dict(os.environ, {
        "EDU_DB_USER": "test_user",
        "EDU_DB_PASSWORD": "test_password",
        "EDU_DB_HOST": "localhost",
        "EDU_DB_PORT": "5432",
        "EDU_DB_NAME": "test_db",
        "ANNU_DB_USER": "test_annuaire_user",
        "ANNU_DB_PASSWORD": "test_annuaire_password",
        "ANNU_DB_HOST": "localhost",
        "ANNU_DB_PORT": "5432",
        "ANNU_DB_NAME": "test_annuaire_db",
    }).start()
