import pytest
from pathlib import Path
from websocket import create_connection
import json
from xprocess import ProcessStarter
import vtk
import os


class ServerMonitor:
    def __init__(self):
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
            reponse = self.ws.recv()

    def call(self, rpc, params=[]):
        print(f"{rpc=}{params=}", flush=True)
        response = self.ws.send(
            json.dumps(
                {
                    "id": f"rpc:test",
                    "method": rpc,
                    "args": params,
                }
            )
        )

    def compare_image(self, nb_messages, path_image):
        self.call("viewport.image.push", [{"size": [300, 300], "view": -1}])
        for i in range(nb_messages):
            image = self.ws.recv()
            print(f"{image=}", flush=True)
        if isinstance(image, bytes):
            response = self.ws.recv()
            print(f"{response=}", flush=True)
            format = json.loads(response)["result"]["format"]
            print(f"{format=}", flush=True)
            test_filename = os.path.abspath(f"tests/tests_output/test.{format}")
            print(f"{test_filename=}", flush=True)
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
        print(f"ROOT_PATH: {self.root_path}")

    def get_xprocess_args(self):
        server_path = "vtkw_server.py"

        class Starter(ProcessStarter):
            terminate_on_interrupt = True
            pattern = "wslink: Starting factory"

            # command to start process
            args = [
                "python3",
                str(self.root_path / server_path),
                "--host",
                "0.0.0.0",
                "--port",
                "1234",
            ]

        return Path(server_path).name, Starter, ServerMonitor


ROOT_PATH = Path(__file__).parent.parent.absolute()
HELPER = FixtureHelper(ROOT_PATH)


@pytest.fixture
def server(xprocess):
    name, Starter, Monitor = HELPER.get_xprocess_args()

    # ensure process is running and return its logfile
    xprocess.ensure(name, Starter)
    yield Monitor()

    # clean up whole process tree afterwards
    xprocess.getinfo(name).terminate()
