import os
from shutil import copyfile, copytree
from sys import platform


def default_config() -> None:
    os.environ["HOST"] = "localhost"
    os.environ["PORT"] = "1234"
    os.environ["PROJECT_FOLDER_PATH"] = "/project/"
    os.environ["DATA_FOLDER_PATH"] = os.path.join(os.environ["PROJECT_FOLDER_PATH"], "data")


def prod_config() -> None:
    default_config()


def dev_config() -> None:
    default_config()
    data_folder_path = os.environ.get("DATA_FOLDER_PATH")
    if data_folder_path and not os.path.exists(data_folder_path):
        os.mkdir(data_folder_path)


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


def test_config() -> None:
    default_config()
    if "DATA_FOLDER_PATH" not in os.environ:
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "data")
        os.environ["DATA_FOLDER_PATH"] = os.path.abspath(data_path)

    data_path = os.environ["DATA_FOLDER_PATH"]
    if not os.path.exists(data_path):
        os.makedirs(data_path, exist_ok=True)

    db_file = os.path.join(data_path, "project.db")
    if not os.path.exists(db_file):
        open(db_file, "a").close()
