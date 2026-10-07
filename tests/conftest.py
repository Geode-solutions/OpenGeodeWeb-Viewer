import contextlib
import json
import logging
import os
import shutil
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any, ClassVar

import pytest
from opengeodeweb_microservice.database.connection import get_session, init_database
from opengeodeweb_microservice.database.data import Data
from vtkmodules.vtkImagingCore import vtkImageDifference
from vtkmodules.vtkIOImage import vtkImageReader2, vtkJPEGReader, vtkPNGReader
from websocket import WebSocketTimeoutException, create_connection
from xprocess import ProcessStarter, XProcess  # type: ignore[import-untyped]

from opengeodeweb_viewer.config import TestConfig
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView

logger = logging.getLogger(__name__)


type RpcTestParams = list[dict[str, Any] | int] | None


class ServerMonitor:
    def __init__(self, log: str, port: str = "1234") -> None:
        self.log = log
        self.ws = create_connection(f"ws://localhost:{port}/ws")
        self.images_dir_path = Path(__file__).parent.resolve() / "data" / "images"
        self.test_output_dir = Path(__file__).parent.resolve() / "tests_output"
        self.test_output_dir.mkdir(exist_ok=True)
        self._init_ws()
        self._drain_initial_messages()

    def call(self, rpc: str, params: RpcTestParams = None) -> None:
        if params is None:
            params = [{}]
        self.ws.send(
            json.dumps(
                {
                    "id": "rpc:" + rpc,
                    "method": rpc,
                    "args": params,
                }
            )
        )

    def print_log(self) -> None:
        output = ""
        with Path(self.log).open() as f:
            for line in f:
                if "@@__xproc_block_delimiter__@@" in line:
                    output = ""
                    continue
                output += line
        logger.info("%s", output)

    def get_response(self) -> bytes | dict[str, object] | str:
        response = self.ws.recv()
        if isinstance(response, bytes):
            return response
        try:
            parsed = json.loads(response)
            if isinstance(parsed, dict):
                return parsed
            return str(parsed)
        except json.JSONDecodeError:
            return str(response)

    @staticmethod
    def _reader_for_file(path: Path) -> vtkImageReader2:
        suffix = path.suffix.lower()
        reader: vtkImageReader2
        if suffix == ".png":
            reader = vtkPNGReader()
        elif suffix in (".jpg", ".jpeg"):
            reader = vtkJPEGReader()
        else:
            msg = f"Unsupported image format for file: {path}"
            raise ValueError(msg)
        reader.SetFileName(str(path))
        return reader

    def images_diff(self, first_image_path: Path, second_image_path: Path) -> float:
        first_reader = self._reader_for_file(first_image_path)
        second_reader = self._reader_for_file(second_image_path)

        images_diff = vtkImageDifference()
        images_diff.SetInputConnection(first_reader.GetOutputPort())
        images_diff.SetImageConnection(second_reader.GetOutputPort())
        images_diff.Update()

        logger.info("thresholded error=%s", images_diff.GetThresholdedError())
        return images_diff.GetThresholdedError()

    def compare_image(self, filename: str) -> bool:
        self.call(
            VtkViewerView.viewer_prefix
            + VtkViewerView.viewer_schemas_dict["render"]["rpc"]
        )
        while True:
            image = self.ws.recv()
            if isinstance(image, bytes):
                response = self.ws.recv()
                logger.info("response=%s", response)
                result = json.loads(response)["result"]
                if result["stale"]:
                    continue
                test_file_path = self.test_output_dir / f"test.{result['format']}"
                test_file_path.write_bytes(image)
                path_image = self.images_dir_path / filename
                return self.images_diff(test_file_path, path_image) == 0.0
            logger.info("response = %s", image)
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
            try:
                self.ws.recv()
            except WebSocketTimeoutException:
                logger.warning(
                    "Timeout on message %s, but continuing to try remaining messages...",
                    i,
                )
                continue


class FixtureHelper:
    def __init__(self, root_path: Path) -> None:
        self.root_path = Path(root_path)

    def get_xprocess_args(self, project_folder_path: str) -> tuple[str, type, type]:
        class Starter(ProcessStarter):  # type: ignore[misc]
            terminate_on_interrupt = True
            pattern = "wslink: Starting factory"
            timeout = 10

            # command to start process
            args: ClassVar[list[str]] = [
                "opengeodeweb-viewer",
                "--project_folder_path",
                project_folder_path,
            ]

        return "app", Starter, ServerMonitor


ROOT_PATH = Path(__file__).parent.parent.absolute()
HELPER = FixtureHelper(ROOT_PATH)
# Data generated by the tests (data folders, project.db) lives in a temporary project folder,
# removed at session end; tests/data only holds the source fixtures.
TEST_PROJECT_FOLDER_PATH = tempfile.mkdtemp(prefix="ogw_test_data_")


@pytest.fixture
def server(xprocess: XProcess) -> Generator[ServerMonitor, None, None]:
    name, starter, monitor_class = HELPER.get_xprocess_args(TEST_PROJECT_FOLDER_PATH)
    os.environ["PYTHON_ENV"] = "test"
    _, log = xprocess.ensure(name, starter)
    monitor = monitor_class(log)
    yield monitor
    with contextlib.suppress(Exception):
        monitor.ws.close()
    xprocess.getinfo(name).terminate()
    monitor.print_log()


@pytest.fixture(scope="session", autouse=True)
def configure_test_environment() -> Generator[None, None, None]:
    app_config = TestConfig(TEST_PROJECT_FOLDER_PATH)
    db_path = Path(app_config.DATA_FOLDER_PATH) / "project.db"
    init_database(db_path=db_path)
    os.environ["TEST_DB_PATH"] = str(db_path)

    yield
    shutil.rmtree(TEST_PROJECT_FOLDER_PATH, ignore_errors=True)
    logger.info("Cleaned up test project folder: %s", TEST_PROJECT_FOLDER_PATH)


@pytest.fixture
def dataset_factory() -> Callable[..., str]:
    def create_dataset(
        *, data_id: str, viewable_file: str, viewer_elements_type: str = "default"
    ) -> str:
        session = get_session()
        viewer_object = "model" if viewable_file.lower().endswith(".vtm") else "mesh"

        row = session.get(Data, data_id)
        if row is None:
            session.add(
                Data(
                    id=data_id,
                    geode_id="00000000-0000-0000-0000-000000000000",
                    viewable_file=viewable_file,
                    geode_object=viewer_object,
                    viewer_object=viewer_object,
                    viewer_elements_type=viewer_elements_type,
                )
            )
        else:
            row.viewable_file = viewable_file
            row.geode_object = viewer_object
            row.viewer_object = viewer_object
            row.viewer_elements_type = viewer_elements_type
        session.commit()

        data_folder = Path(os.environ["DATA_FOLDER_PATH"]) / data_id
        data_folder.mkdir(parents=True, exist_ok=True)

        src_path = Path(__file__).parent / "data" / viewable_file
        dst_path = data_folder / viewable_file
        if not dst_path.exists() or dst_path.resolve() != src_path.resolve():
            shutil.copy(src_path, dst_path)

        if dst_path.suffix.lower() == ".vtm":
            tree = ET.parse(dst_path)  # noqa: S314 trusted test fixture from tests/data
            root = tree.getroot()
            for dataset in root.findall(".//DataSet"):
                file_attr = dataset.get("file")
                if file_attr:
                    src_piece = src_path.parent / file_attr
                    dst_piece = data_folder / file_attr
                    dst_piece.parent.mkdir(parents=True, exist_ok=True)
                    if src_piece.exists():
                        shutil.copy(src_piece, dst_piece)

        return data_id

    return create_dataset
