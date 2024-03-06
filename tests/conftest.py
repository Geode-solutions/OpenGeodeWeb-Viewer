import pytest
from pathlib import Path
from websocket import create_connection
import json
from xprocess import ProcessStarter
import vtk
import os
from src.opengeodeweb_viewer import config


class ServerMonitor:
    def __init__(self, log):
        self.log = log
        self.ws = create_connection("ws://localhost:1234/ws")
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
            reponse = self.ws.recv()

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
        response = eval(self.ws.recv())
        return response

    def compare_image(self, nb_messages, path_image):
        for i in range(nb_messages):
            print(f"{i=}", flush=True)
            image = self.ws.recv()
            if isinstance(image, bytes):
                test_filename = os.path.abspath(f"tests/tests_output/test.jpeg")
                with open(test_filename, "wb") as f:
                    f.write(image)
                    f.close()
        if isinstance(image, bytes):
            print(f"{image=}", flush=True)
            response = self.ws.recv()
            print(f"{response=}", flush=True)
            format = json.loads(response)["result"]["format"]
            test_filename = os.path.abspath(f"tests/tests_output/test.{format}")
            with open(test_filename, "wb") as f:
                f.write(image)
                f.close()

            test_reader = vtk.vtkJPEGReader()
            test_reader.SetFileName(test_filename)

            answer_reader = vtk.vtkJPEGReader()
            answer_reader.SetFileName(path_image)

            images_diff = vtk.vtkImageDifference()
            images_diff.SetInputConnection(test_reader.GetOutputPort())
            images_diff.SetImageConnection(answer_reader.GetOutputPort())
            images_diff.Update()

            print(f"{images_diff.GetThresholdedError()=}")
            return images_diff.GetThresholdedError() == 0.0


class FixtureHelper:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        print(f"{self.root_path=}", flush=True)

    def get_xprocess_args(self):

        server_path = "src/opengeodeweb_viewer/vtkw_server.py"
        print(f"{server_path=}", flush=True)

        class Starter(ProcessStarter):
            terminate_on_interrupt = True
            pattern = "wslink: Starting factory"

            # command to start process
            args = [
                "python3",
                str(self.root_path / server_path),
            ]

        return Path(server_path).name, Starter, ServerMonitor


ROOT_PATH = Path(__file__).parent.parent.absolute()
HELPER = FixtureHelper(ROOT_PATH)


@pytest.fixture
def server(xprocess):
    name, Starter, Monitor = HELPER.get_xprocess_args()
    os.environ["PYTHON_ENV"] = "test"
    config.test_config()
    _, log = xprocess.ensure(name, Starter)
    print(log)
    print("server", os.environ.get("DATA_FOLDER_PATH"), flush=True)
    monitor = Monitor(log)
    yield monitor

    # clean up whole process tree afterwards
    xprocess.getinfo(name).terminate()
    monitor.print_log()
