import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

class DBManager:
    def __init__(self, db_user: str, db_password: str, 
                 db_host: str, db_port: str, db_database: str):
        SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_size=20,  # Number of connections to maintain in the pool
            max_overflow=10,  # Extra connections beyond pool size
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db(self) -> Session:
        """
        Generator that manages the database session.

        This function creates a session with the database via SQLAlchemy, 
        makes it available for the following calls via "yield," and ensures 
        that the session is properly closed once the operation is complete.

        Returns:
        - db: A Session instance to interact with the database.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# Fetch environment variables for database connection
POST_EDU_DB = DBManager(
    db_user = os.environ["EDU_DB_USER"],
    db_password = os.environ["EDU_DB_PASSWORD"],
    db_host = os.environ["EDU_DB_HOST"],
    db_port = os.environ["EDU_DB_PORT"],
    db_database = os.environ["EDU_DB_NAME"],
)

ANNUAIRE_DB = DBManager(
    db_user = os.environ["ANNU_DB_USER"],
    db_password = os.environ["ANNU_DB_PASSWORD"],
    db_host = os.environ["ANNU_DB_HOST"],
    db_port = os.environ["ANNU_DB_PORT"],
    db_database = os.environ["ANNU_DB_NAME"],
)