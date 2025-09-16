import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import Engine

from opengeodeweb_microservice.database.data import Data
from opengeodeweb_microservice.database.base import Base


class DatabaseManager:
    def __init__(self):
        self._engine: Optional[Engine] = None
        self._session_factory = None
        self._scoped_session = None

    def initialize(self, database_path: str):
        if not database_path:
            print("Warning: No database path provided")
            return False

        try:
            self._engine = create_engine(f"sqlite:///{database_path}", echo=False)
            self._session_factory = sessionmaker(bind=self._engine)
            self._scoped_session = scoped_session(self._session_factory)
            print(f"Database initialized at: {database_path}")
            return True

        except Exception as e:
            print(f"Error initializing database: {e}")
            return False

    def get_session(self):
        return self._scoped_session() if self._scoped_session else None

    def close(self):
        if self._scoped_session:
            self._scoped_session.remove()
        if self._engine:
            self._engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()
