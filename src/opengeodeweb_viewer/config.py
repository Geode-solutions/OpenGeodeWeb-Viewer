import os
from shutil import copyfile, copytree


class Config:
    HOST = "localhost"
    PORT = "1234"
    DATABASE_FILENAME = "project.db"

    def __init__(self, project_folder_path: str):
        self.PROJECT_FOLDER_PATH = project_folder_path
        self.DATA_FOLDER_PATH = os.path.join(project_folder_path, "data")
        self.sync_env()

    def sync_env(self) -> None:
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
        os.makedirs(self.DATA_FOLDER_PATH, exist_ok=True)


class TestConfig(Config):
    def __init__(self, project_folder_path: str) -> None:
        print("Received ", project_folder_path, flush=True)
        super().__init__(project_folder_path)
        os.makedirs(self.DATA_FOLDER_PATH, exist_ok=True)
        db_file = os.path.join(self.DATA_FOLDER_PATH, self.DATABASE_FILENAME)
        if not os.path.exists(db_file):
            open(db_file, "a").close()


def _copy_test_assets(
    src_data: str,
    tmp_data_root: str,
    test_ids: list[str],
    valid_exts: set[str],
    uploads_directory: str,
    structure_directory: str,
) -> None:
    for root, directories, files in os.walk(src_data):
        for directory in directories:
            for test_id in test_ids:
                dst = os.path.join(tmp_data_root, test_id, directory)
                copytree(os.path.join(root, directory), dst, dirs_exist_ok=True)
        for file in files:
            if os.path.splitext(file)[1].lower() not in valid_exts:
                continue
            src = os.path.join(root, file)
            for test_id in test_ids:
                copyfile(src, os.path.join(tmp_data_root, test_id, file))
            copyfile(src, os.path.join(structure_directory, file))
            copyfile(src, os.path.join(uploads_directory, file))
