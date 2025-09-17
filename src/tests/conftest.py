import pytest
from pathlib import Path
from websocket import create_connection
import json
from xprocess import ProcessStarter
import vtk
import os
from opengeodeweb_viewer import config
import shutil
from opengeodeweb_viewer.database.connection import db_manager
from opengeodeweb_microservice.database.data import Data
from shutil import copyfile, copytree
import os
from typing import Callable, Optional, List
from websocket import WebSocketTimeoutException


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

    def images_diff(self, first_image_path, second_image_path):
        first_reader = self._reader_for_file(first_image_path)
        first_reader.SetFileName(first_image_path)

        second_reader = self._reader_for_file(second_image_path)
        second_reader.SetFileName(second_image_path)

        images_diff = vtk.vtkImageDifference()
        images_diff.SetInputConnection(first_reader.GetOutputPort())
        images_diff.SetImageConnection(second_reader.GetOutputPort())
        images_diff.Update()

        return images_diff.GetThresholdedError()

    def compare_image(self, filename):
        import time
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
        if not isinstance(image, bytes):
            return False
        test_file_path = os.path.abspath(os.path.join(self.test_output_dir, "test.jpeg"))
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
            new_path = os.path.abspath(os.path.join(self.test_output_dir, f"test.{format}"))
            os.replace(test_file_path, new_path)
            test_file_path = new_path

        path_image = os.path.join(self.images_dir_path, filename)
        return self.images_diff(test_file_path, path_image) == 0.0

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
    base_path = os.path.dirname(__file__)
    config.test_config(base_path)

    tmp_data_path = os.environ.get("DATA_FOLDER_PATH")
    assert tmp_data_path, "DATA_FOLDER_PATH must be set by test_config"
    database_path = os.path.join(tmp_data_path, "project.db")
    os.environ["DATABASE_PATH"] = database_path

    ok = db_manager.initialize(database_path)
    if not ok:
        raise RuntimeError("Failed to initialize test database")

    def _seed_database(session):
        # Seed mesh data: id=123456789 -> hat.vtp
        if session.get(Data, "123456789") is None:
            session.add(
                Data(
                    id="123456789",
                    native_file_name="native.vtp",
                    viewable_file_name="hat.vtp",
                    geode_object="mesh",
                    light_viewable=None,
                    input_file="",
                    additional_files=[],
                )
            )
        # Seed model data: id=12345678 -> CrossSection.vtm
        if session.get(Data, "12345678") is None:
            session.add(
                Data(
                    id="12345678",
                    native_file_name="native.vtm",
                    viewable_file_name="CrossSection.vtm",
                    geode_object="model",
                    light_viewable=None,
                    input_file="",
                    additional_files=[],
                )
            )
        # Seed mesh data: id=44556677 -> points.vtp (tests point set)
        if session.get(Data, "44556677") is None:
            session.add(
                Data(
                    id="44556677",
                    native_file_name="native.vtp",
                    viewable_file_name="points.vtp",
                    geode_object="mesh",
                    light_viewable=None,
                    input_file="",
                    additional_files=[],
                )
            )
        # Seed mesh data: id=22334455 -> edged_curve.vtp (tests edged curve)
        if session.get(Data, "22334455") is None:
            session.add(
                Data(
                    id="22334455",
                    native_file_name="native.vtp",
                    viewable_file_name="edged_curve.vtp",
                    geode_object="mesh",
                    light_viewable=None,
                    input_file="",
                    additional_files=[],
                )
            )
        # Seed mesh data: id=11223344 -> hybrid_solid.vtu (polyèdres)
        if session.get(Data, "11223344") is None:
            session.add(
                Data(
                    id="11223344",
                    native_file_name="native.vtu",
                    viewable_file_name="hybrid_solid.vtu",
                    geode_object="mesh",
                    light_viewable=None,
                    input_file="",
                    additional_files=[],
                )
            )
        # Seed mesh data: id=33445566 -> polygon_attribute.vtp
        if session.get(Data, "33445566") is None:
            session.add(
                Data(
                    id="33445566",
                    native_file_name="native.vtp",
                    viewable_file_name="polygon_attribute.vtp",
                    geode_object="mesh",
                    light_viewable=None,
                    input_file="",
                    additional_files=[],
                )
            )
        # Seed mesh data: id=33445577 -> vertex_attribute.vtp
        if session.get(Data, "33445577") is None:
            session.add(
                Data(
                    id="33445577",
                    native_file_name="native.vtp",
                    viewable_file_name="vertex_attribute.vtp",
                    geode_object="mesh",
                    light_viewable=None,
                    input_file="",
                    additional_files=[],
                )
            )

    session = db_manager.get_session()
    try:
        _seed_database(session)
        session.commit()
    finally:
        session.close()

    yield
    tmp_data_path = os.environ.get("DATA_FOLDER_PATH")
    if tmp_data_path and "ogw_test_data_" in tmp_data_path:
        shutil.rmtree(tmp_data_path, ignore_errors=True)
        print(f"Cleaned up test data folder: {tmp_data_path}", flush=True)


@pytest.fixture
def dataset_factory() -> Callable[..., str]:
    base_path = os.path.dirname(__file__)
    src_data = os.path.join(base_path, "data")
    data_root = os.environ.get("DATA_FOLDER_PATH")
    assert data_root, "DATA_FOLDER_PATH undefined"

    def create_dataset(
        *,
        id: str,
        geode_object: str,
        viewable_file_name: str,
        native_file_name: Optional[str] = None,
        additional_files: Optional[List[str]] = None,
        light_viewable: Optional[bool] = None,
        input_file: Optional[str] = None,
    ) -> str:
        dest_dir = os.path.join(data_root, id)
        os.makedirs(dest_dir, exist_ok=True)

        def _copy_asset(fname: str):
            src = os.path.join(src_data, fname)
            dst = os.path.join(dest_dir, fname)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.isdir(src):
                copytree(src, dst, dirs_exist_ok=True)
            else:
                copyfile(src, dst)

        _copy_asset(viewable_file_name)
        if native_file_name:
            native_src = os.path.join(src_data, native_file_name)
            if os.path.exists(native_src):
                _copy_asset(native_file_name)
        for fname in additional_files or []:
            _copy_asset(fname)

        with db_manager.session_scope() as session:
            row = session.get(Data, id)
            if row is None:
                session.add(
                    Data(
                        id=id,
                        native_file_name=native_file_name or "",
                        viewable_file_name=viewable_file_name,
                        geode_object=geode_object,
                        light_viewable=light_viewable,
                        input_file=input_file or "",
                        additional_files=additional_files or [],
                    )
                )
            else:
                row.native_file_name = native_file_name or row.native_file_name
                row.viewable_file_name = viewable_file_name or row.viewable_file_name
                row.geode_object = geode_object or row.geode_object
                row.light_viewable = light_viewable if light_viewable is not None else row.light_viewable
                row.input_file = input_file or row.input_file
                row.additional_files = additional_files or row.additional_files
        return id

    return create_dataset
