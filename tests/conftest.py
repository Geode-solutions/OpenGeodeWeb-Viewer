import pytest
from pathlib import Path
from websocket import create_connection
import json
from xprocess import ProcessStarter
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch
from vtkmodules.test.Testing import compareImageWithSavedImage


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
        for i in range(nb_messages):
            print(f"{i=}", flush=True)
            response = self.ws.recv()
            if isinstance(response, bytes):
                print("isinstance")
                with open(path_image, "wb") as img:
                    img.write(response)
                    img.close()
        print(compareImageWithSavedImage(path_image, saved_image))
        # compare with path_image


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
