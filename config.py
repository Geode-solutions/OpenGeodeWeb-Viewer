import os
from sys import platform


def default_config():
    print("default_config")
    os.environ["HOST"] = "0.0.0.0"
    os.environ["PORT"] = "1234"


def prod_config():
    default_config()
    print("prod_config")
    os.environ["DATA_FOLDER_PATH"] = "/data/"


def dev_config():
    default_config()
    print("dev_config")
    if platform == "linux":
        os.environ["DATA_FOLDER_PATH"] = "/temp/OpenGeodeWeb_Data/"
    elif platform == "win32":
        print(f"{os.getlogin()=}")
        os.environ["DATA_FOLDER_PATH"] = os.path.join(
            "C:/Users/", os.getlogin(), "/OpenGeodeWeb_Data/"
        )


def test_config():
    default_config()
    print("test_config")
    os.environ["DATA_FOLDER_PATH"] = os.path.abspath("./tests/data/")
