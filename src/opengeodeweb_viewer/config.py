import os
import tempfile
from shutil import copyfile, copytree
from sys import platform


def default_config():
    os.environ["DEFAULT_HOST"] = "localhost"
    os.environ["DEFAULT_PORT"] = "1234"


def prod_config():
    default_config()
    os.environ["DATA_FOLDER_PATH"] = "/data/"


def dev_config():
    default_config()
    if platform == "linux":
        os.environ["DATA_FOLDER_PATH"] = "/temp/OpenGeodeWeb_Data/"
    elif platform == "win32":
        os.environ["DATA_FOLDER_PATH"] = os.path.join(
            "C:/Users", os.getlogin(), "OpenGeodeWeb_Data"
        )
    if not os.path.exists(os.environ.get("DATA_FOLDER_PATH")):
        os.mkdir(os.environ.get("DATA_FOLDER_PATH"))


def test_config(path):
    default_config()

    tmp_data_root = tempfile.mkdtemp(prefix="ogw_test_data_")
    os.environ["DATA_FOLDER_PATH"] = tmp_data_root

    src_data = os.path.join(path, "data")
    if not os.path.isdir(src_data):
        raise FileNotFoundError(f"Test data folder not found: {src_data}")

    test_ids = ["123456789", "12345678"]
    valid_exts = {".vtp", ".vti", ".vtu", ".vtm"}

    project_uuid = "test-project-uuid"
    data_uuid = "test-data-uuid"
    uploads_directory = os.path.join(tmp_data_root, project_uuid, "uploads")
    structure_directory = os.path.join(tmp_data_root, project_uuid, data_uuid)

    for directory in [
        *test_ids,
        uploads_directory,
        structure_directory,
    ]:  # create directories for tests
        os.makedirs(
            (
                os.path.join(tmp_data_root, directory)
                if isinstance(directory, str)
                else directory
            ),
            exist_ok=True,
        )

    for root, directories, files in os.walk(src_data):
        for directory in directories:
            dst = os.path.join(tmp_data_root, test_ids[0], directory)
            copytree(os.path.join(root, directory), dst, dirs_exist_ok=True)

        for file in files:
            if os.path.splitext(file)[1].lower() not in valid_exts:
                continue

            src = os.path.join(root, file)
            for test_id in test_ids:
                copyfile(src, os.path.join(tmp_data_root, test_id, file))
            copyfile(src, os.path.join(structure_directory, file))
            copyfile(src, os.path.join(uploads_directory, file))

    print(f"\nDATA_FOLDER_PATH set to: {tmp_data_root}", flush=True)
