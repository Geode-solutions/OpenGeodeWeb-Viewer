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

    original_data_path = os.path.join(path, "data")
    if not os.path.exists(original_data_path):
        raise FileNotFoundError(f"Test data folder not found: {original_data_path}")

    valid_extensions = {".vtp", ".vti", ".vtu", ".vtm", ".png", ".jpeg", ".jpg"}
    
    test_ids = ["123456789", "12345678"]
    
    for test_id in test_ids:
        test_id_dir = os.path.join(tmp_data_root, test_id)
        os.makedirs(test_id_dir, exist_ok=True)
    
    test_project_uuid = "test-project-uuid"
    test_data_uuid = "test-data-uuid"
    new_structure_dir = os.path.join(tmp_data_root, test_project_uuid, test_data_uuid)
    os.makedirs(new_structure_dir, exist_ok=True)
    
    uploads_dir = os.path.join(tmp_data_root, test_project_uuid, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    for root, dirs, files in os.walk(original_data_path):
        for d in dirs:
            src_dir = os.path.join(root, d)
            dst_dir = os.path.join(tmp_data_root, test_ids[0], d)
            if not os.path.exists(dst_dir):
                copytree(src_dir, dst_dir, dirs_exist_ok=True)

        for file_name in files:
            ext = os.path.splitext(file_name)[1].lower()
            if ext not in valid_extensions:
                continue

            full_path = os.path.join(root, file_name)
            
            for test_id in test_ids:
                test_id_dst = os.path.join(tmp_data_root, test_id, file_name)
                copyfile(full_path, test_id_dst)
            
            new_structure_dst = os.path.join(new_structure_dir, file_name)
            copyfile(full_path, new_structure_dst)
            
            uploads_dst = os.path.join(uploads_dir, file_name)
            copyfile(full_path, uploads_dst)

    print(f"\n✅ DATA_FOLDER_PATH set to: {tmp_data_root}", flush=True)
