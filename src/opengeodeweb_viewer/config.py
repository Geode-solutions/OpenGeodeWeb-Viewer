import os
from sys import platform


def default_config():
    os.environ["HOST"] = "0.0.0.0"
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


def test_config():
    default_config()
    print(f"{os.path.dirname(__file__)=}", flush=True)
    os.environ["DATA_FOLDER_PATH"] = os.path.join(
        os.path.dirname(__file__), "..", "tests", "data"
    )
