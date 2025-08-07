import pytest
from pathlib import Path
from websocket import create_connection
import json
from xprocess import ProcessStarter
import vtk
import os
from opengeodeweb_viewer import config
import shutil


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
        for i in range(5):
            print(f"{i=}", flush=True)
            response = self.ws.recv()
            print(f"{response=}", flush=True)

    def call(self, rpc, params=[{}]):
        print(f"{rpc=} {params=}", flush=True)
        response = self.ws.send(
            json.dumps(
                {
                    "id": f"rpc:test",
                    "method": rpc,
                    "args": params,
                }
            )
        )
        return response

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
        else:
            return eval(response)

    def images_diff(self, first_image_path, second_image_path):
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

    def compare_image(self, nb_messages, filename):
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


class FixtureHelper:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        print(f"{self.root_path=}", flush=True)

    def get_xprocess_args(self):

        server_path = "opengeodeweb_viewer/vtkw_server.py"
        print(f"{server_path=}", flush=True)

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
    print(log)
    monitor = Monitor(log)
    yield monitor

    # clean up whole process tree afterwards
    xprocess.getinfo(name).terminate()
    monitor.print_log()


@pytest.fixture(scope="session", autouse=True)
def configure_test_environment():
    base_path = os.path.dirname(__file__)
    config.test_config(base_path)
    yield
    tmp_data_path = os.environ.get("DATA_FOLDER_PATH")
    if tmp_data_path and "ogw_test_data_" in tmp_data_path:
        shutil.rmtree(tmp_data_path, ignore_errors=True)
        print(f"Cleaned up test data folder: {tmp_data_path}", flush=True)
