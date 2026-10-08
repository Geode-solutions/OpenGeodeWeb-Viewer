import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class Config:
    HOST = "localhost"
    PORT = "1234"
    DATABASE_FILENAME = "project.db"

    def __init__(self, project_folder_path: str) -> None:
        self.PROJECT_FOLDER_PATH = project_folder_path
        self.DATA_FOLDER_PATH = str(Path(project_folder_path) / "data")
        self.sync_env()

    def sync_env(self) -> None:
        logger.info("PROJECT_FOLDER_PATH=%s", self.PROJECT_FOLDER_PATH)
        logger.info("DATA_FOLDER_PATH=%s", self.DATA_FOLDER_PATH)
        os.environ["PROJECT_FOLDER_PATH"] = self.PROJECT_FOLDER_PATH
        os.environ["DATA_FOLDER_PATH"] = self.DATA_FOLDER_PATH
        os.environ["HOST"] = self.HOST
        os.environ["PORT"] = self.PORT
        os.environ["DATABASE_FILENAME"] = self.DATABASE_FILENAME


class ProdConfig(Config):
    def __init__(self, project_folder_path: str) -> None:
        super().__init__(project_folder_path)


class DevConfig(Config):
    def __init__(self, project_folder_path: str) -> None:
        super().__init__(project_folder_path)
        Path(self.DATA_FOLDER_PATH).mkdir(parents=True, exist_ok=True)


class TestConfig(Config):
    def __init__(self, project_folder_path: str) -> None:
        logger.info("Received %s", project_folder_path)
        super().__init__(project_folder_path)
        Path(self.DATA_FOLDER_PATH).mkdir(parents=True, exist_ok=True)
        (Path(self.DATA_FOLDER_PATH) / self.DATABASE_FILENAME).touch()
