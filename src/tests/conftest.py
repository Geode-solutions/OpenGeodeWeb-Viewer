import pytest
from pathlib import Path
from websocket import create_connection, WebSocketTimeoutException
import json
from xprocess import ProcessStarter
import vtk
import os
import shutil
import xml.etree.ElementTree as ET
from typing import Callable, Generator
from opengeodeweb_viewer import config
from opengeodeweb_microservice.database.connection import get_session, init_database
from opengeodeweb_microservice.database.data import Data

type RpcTestParams = list[
    dict[str, str | int | float | bool | dict[str, int] | list[str]] | int
] | None


class ServerMonitor:
    def __init__(self, log: str) -> None:
        self.log = log
        self.ws = create_connection("ws://localhost:1234/ws")
        self.images_dir_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "data", "images")
        )
        self.test_output_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "tests_output")
        )
        if not os.path.exists(self.test_output_dir):
            os.mkdir(self.test_output_dir)
        self._init_ws()
        self._drain_initial_messages()

    def call(self, rpc: str, params: RpcTestParams = None) -> None:
        if params is None:
            params = [{}]
        self.ws.send(
            json.dumps(
                {
                    "id": "rpc:test",
                    "method": rpc,
                    "args": params,
                }
            )
        )

    def print_log(self) -> None:
        output = ""
        with open(self.log) as f:
            for line in f:
                if "@@__xproc_block_delimiter__@@" in line:
                    output = ""
                    continue
                output += line
        print(output)

    def get_response(self) -> bytes | dict[str, object] | str:
        response = self.ws.recv()
        if isinstance(response, bytes):
            return response
        try:
            parsed = json.loads(response)
            if isinstance(parsed, dict):
                return parsed
            else:
                return str(parsed)
        except Exception:
            return str(response)

    @staticmethod
    def _reader_for_file(path: str) -> vtk.vtkImageReader2:
        lower = path.lower()
        if lower.endswith(".png"):
            return vtk.vtkPNGReader()
        if lower.endswith(".jpg") or lower.endswith(".jpeg"):
            return vtk.vtkJPEGReader()
        return vtk.vtkJPEGReader()

    def images_diff(self, first_image_path: str, second_image_path: str) -> float:
        if ".png" in first_image_path:
            first_reader = vtk.vtkPNGReader()
        elif (".jpg" in first_image_path) or (".jpeg" in first_image_path):
            first_reader = vtk.vtkJPEGReader()
        first_reader.SetFileName(first_image_path)

        if ".png" in second_image_path:
            second_reader = vtk.vtkPNGReader()
        elif (".jpg" in second_image_path) or (".jpeg" in second_image_path):
            second_reader = vtk.vtkJPEGReader()
        second_reader.SetFileName(second_image_path)

        images_diff = vtk.vtkImageDifference()
        images_diff.SetInputConnection(first_reader.GetOutputPort())
        images_diff.SetImageConnection(second_reader.GetOutputPort())
        images_diff.Update()

        print(f"{images_diff.GetThresholdedError()=}")
        return images_diff.GetThresholdedError()

    def compare_image(self, nb_messages: int, filename: str) -> bool:
        for message in range(nb_messages):
            print(f"{message=}", flush=True)
            image = self.ws.recv()
            if isinstance(image, bytes):
                test_file_path = os.path.abspath(
                    os.path.join(self.test_output_dir, "test.jpeg")
                )
                with open(test_file_path, "wb") as f:
                    f.write(image)
                    f.close()
        if isinstance(image, bytes):
            response = self.ws.recv()
            print(f"{response=}", flush=True)
            format = json.loads(response)["result"]["format"]
            test_file_path = os.path.abspath(
                os.path.join(self.test_output_dir, f"test.{format}")
            )
            with open(test_file_path, "wb") as f:
                f.write(image)
                f.close()
            path_image = os.path.join(self.images_dir_path, filename)
            return self.images_diff(test_file_path, path_image) == 0.0
        return False

    def _init_ws(self) -> None:
        self.ws.send(
            json.dumps(
                {
                    "id": "system:hello",
                    "method": "wslink.hello",
                    "args": [{"secret": "wslink-secret"}],
                }
            )
        )
        self.call("viewport.image.push.observer.add", [-1])

    def _drain_initial_messages(
        self, max_messages: int = 5, timeout: float = 10.0
    ) -> None:
        self.ws.settimeout(timeout)
        for i in range(max_messages):
            print(f"{i=}", flush=True)
            try:
                response = self.ws.recv()
                print(f"{response=}", flush=True)
            except WebSocketTimeoutException:
                print(
                    f"Timeout on message {i}, but continuing to try remaining messages...",
                    flush=True,
                )
                continue


class FixtureHelper:
    def __init__(self, root_path: Path) -> None:
        self.root_path = Path(root_path)

    def get_xprocess_args(self) -> tuple[str, type, type]:
        class Starter(ProcessStarter):
            terminate_on_interrupt = True
            pattern = "wslink: Starting factory"
            timeout = 5

            # command to start process
            args = [
                "opengeodeweb-viewer",
            ]

        return "vtkw_server", Starter, ServerMonitor


ROOT_PATH = Path(__file__).parent.parent.absolute()
HELPER = FixtureHelper(ROOT_PATH)


@pytest.fixture
def server(xprocess: object) -> Generator[ServerMonitor, None, None]:
    name, Starter, Monitor = HELPER.get_xprocess_args()
    os.environ["PYTHON_ENV"] = "test"
    _, log = xprocess.ensure(name, Starter)
    monitor = Monitor(log)
    yield monitor
    try:
        monitor.ws.close()
    except Exception:
        pass
    xprocess.getinfo(name).terminate()
    monitor.print_log()


@pytest.fixture(scope="session", autouse=True)
def configure_test_environment() -> Generator[None, None, None]:
    project_root = Path(__file__).parent.parent.parent.absolute()
    os.environ["DATA_FOLDER_PATH"] = str(project_root / "tests" / "data")

    config.test_config()
    db_path = Path(os.environ["DATA_FOLDER_PATH"]) / "project.db"
    init_database(db_path=str(db_path))
    os.environ["TEST_DB_PATH"] = str(db_path)

    yield
    tmp_data_path = os.environ.get("DATA_FOLDER_PATH")
    if tmp_data_path and "ogw_test_data_" in tmp_data_path:
        shutil.rmtree(tmp_data_path, ignore_errors=True)
        print(f"Cleaned up test data folder: {tmp_data_path}", flush=True)


@pytest.fixture
def dataset_factory() -> Callable[..., str]:
    def create_dataset(*, id: str, viewable_file_name: str) -> str:
        session = get_session()
        viewer_object = (
            "model" if viewable_file_name.lower().endswith(".vtm") else "mesh"
        )

        row = session.get(Data, id)
        if row is None:
            session.add(
                Data(
                    id=id,
                    viewable_file_name=viewable_file_name,
                    geode_object=viewer_object,
                    viewer_object=viewer_object,
                )
            )
        else:
            row.viewable_file_name = viewable_file_name
            row.geode_object = viewer_object
            row.viewer_object = viewer_object
        session.commit()

        data_folder = Path(os.environ["DATA_FOLDER_PATH"]) / id
        data_folder.mkdir(parents=True, exist_ok=True)

        src_path = Path(__file__).parent / "data" / viewable_file_name
        dst_path = data_folder / viewable_file_name
        if not dst_path.exists() or dst_path.resolve() != src_path.resolve():
            shutil.copy(src_path, dst_path)

        if dst_path.suffix.lower() == ".vtm":
            tree = ET.parse(dst_path)
            root = tree.getroot()
            for dataset in root.findall(".//DataSet"):
                file_attr = dataset.get("file")
                if file_attr:
                    src_piece = src_path.parent / file_attr
                    dst_piece = data_folder / file_attr
                    dst_piece.parent.mkdir(parents=True, exist_ok=True)
                    if src_piece.exists():
                        shutil.copy(src_piece, dst_piece)

        return id

    return create_dataset
