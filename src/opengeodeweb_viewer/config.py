import os
from glob import glob
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

    legacy_id = "123456789"
    legacy_dir = os.path.join(tmp_data_root, legacy_id)
    os.makedirs(legacy_dir, exist_ok=True)

    for root, dirs, files in os.walk(original_data_path):
        rel_root = os.path.relpath(root, original_data_path)

        # Copier sous-dossiers (comme cube/) dans leur ensemble
        for d in dirs:
            src_dir = os.path.join(root, d)
            dst_dir = os.path.join(tmp_data_root, legacy_id, d)
            if not os.path.exists(dst_dir):
                copytree(src_dir, dst_dir, dirs_exist_ok=True)
                print(f"📦 Copied folder: {src_dir} → {dst_dir}", flush=True)

        for file_name in files:
            ext = os.path.splitext(file_name)[1].lower()
            if ext not in valid_extensions:
                continue

            full_path = os.path.join(root, file_name)
            uuid = os.path.splitext(file_name)[0]

            # uuid/filename
            dst_dir = os.path.join(tmp_data_root, uuid)
            os.makedirs(dst_dir, exist_ok=True)
            dst = os.path.join(dst_dir, file_name)
            copyfile(full_path, dst)

            # legacy path: 123456789/filename
            legacy_dst = os.path.join(legacy_dir, file_name)
            copyfile(full_path, legacy_dst)

            # root-level copy
            root_level_dst = os.path.join(tmp_data_root, file_name)
            copyfile(full_path, root_level_dst)

            print(f"📄 Copied file: {full_path} → {root_level_dst}", flush=True)

    print(f"\n✅ DATA_FOLDER_PATH set to: {tmp_data_root}", flush=True)
