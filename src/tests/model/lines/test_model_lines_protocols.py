# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.model.lines.model_lines_protocols import (
    VtkModelLinesView,
)

# Local application imports
from tests.model.test_model_protocols import test_register_model_cube
from tests.conftest import ServerMonitor


def test_lines_edges_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    server.call(
        VtkModelLinesView.model_lines_prefix
        + VtkModelLinesView.model_lines_schemas_dict["visibility"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(1, 50)),
                "visibility": False,
            }
        ],
    )
    assert server.compare_image(3, "model/cube_visibility_false.jpeg") == True

    server.call(
        VtkModelLinesView.model_lines_prefix
        + VtkModelLinesView.model_lines_schemas_dict["visibility"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(14, 35)),
                "visibility": True,
            }
        ],
    )
    assert server.compare_image(3, "model/lines/visibility.jpeg") == True


def test_lines_edges_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_lines_edges_visibility(server, dataset_factory)

    server.call(
        VtkModelLinesView.model_lines_prefix
        + VtkModelLinesView.model_lines_schemas_dict["color"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(14, 35)),
                "color": {"r": 255, "g": 0, "b": 0},
            }
        ],
    )
    assert server.compare_image(3, "model/lines/color.jpeg") == True
