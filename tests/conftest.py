import pytest
from pathlib import Path

# from trame_client.utils.testing import FixtureHelper
import json
from pathlib import Path
from xprocess import ProcessStarter
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch


# ---------------------------------------------------------
# Pytest helpers
# ---------------------------------------------------------


class TrameServerMonitor:
    def __init__(self, log_path):
        self._log_path = log_path
        self._last_state = {}
        self.port = 0
        self.update()

    def update(self):
        last_state_line = "STATE: {}"
        with open(self._log_path, "r") as f:
            for line in f.readlines():
                print(line)
                if "SERVER_PORT:" in line:
                    self.port = int(line[13:])
                if line[:7] == "STATE: ":
                    last_state_line = line

        self._last_state = json.loads(last_state_line[7:])

    def get_state(self):
        self.update()
        return self._last_state

    def get(self, name):
        self.update()
        return self._last_state.get(name)


def print_state(**kwargs):
    print("STATE:", json.dumps(kwargs), flush=True)


def enable_testing(server, *state_monitor):
    server.state.change(*state_monitor)(print_state)

    @server.controller.add("on_server_ready")
    def print_server_port(**kwargs):
        print("SERVER_PORT:", server.port, flush=True)

    return server


class FixtureHelper:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        print(f"ROOT_PATH: {self.root_path}")

    def remove_page_urls(self):
        BASE_PATH = self.root_path / "visual_baseline"
        for file in BASE_PATH.glob("**/page_url.txt"):
            file.unlink()
            print(f" - remove: {file}")

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

        return Path(server_path).name, Starter, TrameServerMonitor


ROOT_PATH = Path(__file__).parent.parent.absolute()
HELPER = FixtureHelper(ROOT_PATH)


@pytest.fixture
def server(xprocess):
    name, Starter, Monitor = HELPER.get_xprocess_args()

    # ensure process is running and return its logfile
    logfile = xprocess.ensure(name, Starter)
    yield Monitor(logfile[1])

    # clean up whole process tree afterwards
    xprocess.getinfo(name).terminate()
