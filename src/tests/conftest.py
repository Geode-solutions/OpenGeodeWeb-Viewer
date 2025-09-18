import pytest
from pathlib import Path
from websocket import create_connection, WebSocketTimeoutException
import json
from xprocess import ProcessStarter
import vtk
import os
import shutil
import time
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Callable
from opengeodeweb_viewer import config
from opengeodeweb_microservice.database.connection import get_session, init_database
from opengeodeweb_microservice.database.data import Data


class ServerMonitor:
    def __init__(self, log):
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

    def call(self, rpc, params=[{}]):
        return self.ws.send(
            json.dumps(
                {
                    "id": "rpc:test",
                    "method": rpc,
                    "args": params,
                }
            )
        )

    def print_log(self):
        output = ""
        with open(self.log) as f:
            for line in f:
                if "@@__xproc_block_delimiter__@@" in line:
                    output = ""
                    continue
                output += line
        print(output)

    def get_response(self):
        response = self.ws.recv()
        if isinstance(response, bytes):
            return response
        try:
            return json.loads(response)
        except Exception:
            return response

    @staticmethod
    def _reader_for_file(path: str):
        lower = path.lower()
        if lower.endswith(".png"):
            return vtk.vtkPNGReader()
        if lower.endswith(".jpg") or lower.endswith(".jpeg"):
            return vtk.vtkJPEGReader()
        return vtk.vtkJPEGReader()

    def images_diff(self, first_image_path, second_image_path, tolerance: float = 0.0):
        first_reader = self._reader_for_file(first_image_path)
        first_reader.SetFileName(first_image_path)

        second_reader = self._reader_for_file(second_image_path)
        second_reader.SetFileName(second_image_path)

        images_diff = vtk.vtkImageDifference()
        images_diff.SetInputConnection(first_reader.GetOutputPort())
        images_diff.SetImageConnection(second_reader.GetOutputPort())
        images_diff.Update()

        error = images_diff.GetThresholdedError()
        print(f"Image comparison error for {second_image_path}: {error} (tolerance: {tolerance})", flush=True)
        return error <= tolerance

    def compare_image(self, nb_messages, filename, tolerance=0.0):

        self.ws.settimeout(4.0)
        image = None
        deadline = time.time() + 12.0
        while time.time() < deadline:
            try:
                msg = self.ws.recv()
            except WebSocketTimeoutException:
                continue
            if isinstance(msg, bytes):
                image = msg
                break
        if not isinstance(msg, bytes):
            return False
        test_file_path = os.path.abspath(
            os.path.join(self.test_output_dir, "test.jpeg")
        )
        with open(test_file_path, "wb") as f:
            f.write(image)
        format = "jpeg"
        try:
            meta = self.ws.recv()
            try:
                format = json.loads(meta)["result"]["format"]
            except Exception:
                pass
        except WebSocketTimeoutException:
            pass

        if format != "jpeg":
            new_path = os.path.abspath(
                os.path.join(self.test_output_dir, f"test.{format}")
            )
            os.replace(test_file_path, new_path)
            test_file_path = new_path

        path_image = os.path.join(self.images_dir_path, filename)
        return self.images_diff(test_file_path, path_image, tolerance)

    def _init_ws(self):
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

    def _drain_initial_messages(self, max_messages: int = 5, timeout: float = 4.0):

        self.ws.settimeout(timeout)
        for _ in range(max_messages):
            try:
                _ = self.ws.recv()
            except WebSocketTimeoutException:
                break

    def print_log(self):
        output = ""
        with open(self.log) as f:
            for line in f:
                if "@@__xproc_block_delimiter__@@" in line:
                    output = ""
                    continue
                output += line
        print(output)


class FixtureHelper:
    def __init__(self, root_path):
        self.root_path = Path(root_path)

    def get_xprocess_args(self):
        class Starter(ProcessStarter):
            terminate_on_interrupt = True
            pattern = "wslink: Starting factory"
            timeout = 5

            # command to start process
            args = [
                "opengeodeweb_viewer",
            ]

        return "vtkw_server", Starter, ServerMonitor


ROOT_PATH = Path(__file__).parent.parent.absolute()
HELPER = FixtureHelper(ROOT_PATH)


@pytest.fixture
def server(xprocess):
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
def configure_test_environment():
    base_path = Path(__file__).parent
    config.test_config(base_path)
    db_path = base_path / "project.db"
    init_database(db_path=str(db_path))
    os.environ["TEST_DB_PATH"] = str(db_path)

    yield
    tmp_data_path = os.environ.get("DATA_FOLDER_PATH")
    if tmp_data_path and "ogw_test_data_" in tmp_data_path:
        shutil.rmtree(tmp_data_path, ignore_errors=True)
        print(f"Cleaned up test data folder: {tmp_data_path}", flush=True)


@pytest.fixture
def dataset_factory() -> Callable[..., str]:

    def create_dataset(
        *, id: str, viewable_file_name: str, geode_object: str = None
    ) -> str:
        session = get_session()
        if geode_object is None:
            geode_object = (
                "model" if viewable_file_name.lower().endswith(".vtm") else "mesh"
            )

        row = session.get(Data, id)
        if row is None:
            session.add(
                Data(
                    id=id,
                    native_file_name="",
                    viewable_file_name=viewable_file_name,
                    geode_object=geode_object,
                    light_viewable=None,
                    input_file="",
                    additional_files=[],
                )
            )
        else:
            row.viewable_file_name = viewable_file_name
            row.geode_object = geode_object
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
