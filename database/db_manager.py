from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.schema import CreateSchema


from models.base import Base, SCHEMA_NAME


class DatabaseManager:

    def __init__(self, database_url: str):
        
        self.engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False
        )

    def create_schema(self) -> None:
        """
        Creates the application schema if it does not exist.
        """
        with self.engine.begin() as connection:
            connection.execute(
                CreateSchema(
                    SCHEMA_NAME,
                    if_not_exists=True
                )
            )

    def create_tables(self) -> None:
        """
        Creates the application schema and all tables defined
        in the SQLAlchemy metadata.
        """
        self.create_schema()

        Base.metadata.create_all(
            bind=self.engine
        )

    def create_session(self) -> Session:
        """
        Creates and returns a new database session.
        """
        return self.SessionLocal()

    def close(self) -> None:
        """
        Disposes the database engine and its connection pool.
        """
        self.engine.dispose()