import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import URL
import logging
import traceback

logger = logging.getLogger(__name__)


class DBManager:
    def __init__(self, db_user: str, db_password: str, 
                 db_host: str, db_port: str, db_database: str
                 ):
        """
        Initializes the DBManager with the connection details for the database.
        
        Args:
            db_user (str): Database user.
            db_password (str): Database password.
            db_host (str): Database host.
            db_port (str): Database port.
            db_database (str): Database name.
        """
        self.db_database = db_database

        sqlalchemy_database_url = URL.create(
            "postgresql+psycopg2",
            username=db_user,
            password=db_password,
            host=db_host,
            database=db_database,
            port=db_port
        )
        try:
            self.engine = create_engine(
                sqlalchemy_database_url,
                pool_size=20,
                max_overflow=10,
            )
            logger.info(f"Successfully initialized DBManager for database '{db_database}'.")
        except Exception as e:
            logger.error(f"Failed to initialize DBManager for database '{db_database}': {traceback.format_exc()}")
            raise 

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_db(self) -> Session:
        """
        Yields a database session, ensuring it is properly closed after use.
        
        Yields:
            Session: A SQLAlchemy session instance to interact with the database.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
            logger.info(f"Closed session for database '{self.db_database}'.")

try:
    POST_DB = DBManager(
        db_user=os.environ["EDU_DB_USER"],
        db_password=os.environ["EDU_DB_PASSWORD"],
        db_host=os.environ["EDU_DB_HOST"],
        db_port=os.environ["EDU_DB_PORT"],
        db_database=os.environ["EDU_DB_NAME"]
    )

    ANNUAIRE_DB = DBManager(
        db_user=os.environ["ANNU_DB_USER"],
        db_password=os.environ["ANNU_DB_PASSWORD"],
        db_host=os.environ["ANNU_DB_HOST"],
        db_port=os.environ["ANNU_DB_PORT"],
        db_database=os.environ["ANNU_DB_NAME"]
    )
except RuntimeError as e:
    logger.critical(f"Failed to initialize database managers: {e}")
    raise
