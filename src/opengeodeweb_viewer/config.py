import os
from shutil import copyfile, copytree
from sys import platform


def default_config() -> None:
    os.environ["DEFAULT_HOST"] = "localhost"
    os.environ["DEFAULT_PORT"] = "1234"


def prod_config() -> None:
    default_config()
    os.environ["DATA_FOLDER_PATH"] = "/data/"


def dev_config() -> None:
    default_config()
    if platform == "linux":
        os.environ["DATA_FOLDER_PATH"] = "/temp/OpenGeodeWeb_Data/"
    elif platform == "win32":
        os.environ["DATA_FOLDER_PATH"] = os.path.join(
            "C:/Users", os.getlogin(), "OpenGeodeWeb_Data"
        )
    if not os.path.exists(os.environ.get("DATA_FOLDER_PATH")):
        os.mkdir(os.environ.get("DATA_FOLDER_PATH"))


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
