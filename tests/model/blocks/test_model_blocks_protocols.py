# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.model.blocks.model_blocks_protocols import (
    VtkModelBlocksView,
)
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView

# Local application imports
from tests.model.test_model_protocols import test_register_model_cube
from tests.conftest import ServerMonitor

# Local constants
model_id = "12345678901234567890123456789012"


def test_blocks_polyhedra_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["visibility"]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": list(range(1, 50)),
                "visibility": False,
            }
        ],
    )

    assert server.compare_image("model/cube_visibility_false.jpeg") == True

    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["visibility"]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": list(range(48, 50)),
                "visibility": True,
            }
        ],
    )

    assert server.compare_image("model/blocks/visibility.jpeg") == True


def test_blocks_polyhedra_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_blocks_polyhedra_visibility(server, dataset_factory)

    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["color"]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": list(range(48, 50)),
                "color_mode": "constant",
                "color": {"red": 255, "green": 0, "blue": 0, "alpha": 1.0},
            }
        ],
    )
    assert server.compare_image("model/blocks/color.jpeg") == True


def test_blocks_clipping_plane(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["clipping_planes"]["rpc"],
        [
            {
                "ids": [model_id],
                "planes": [
                    {
                        "origin": [5.0, 5.0, 5.0],
                        "normal": [1.0, 1.0, 1.0],
                    }
                ],
            }
        ],
    )
    assert server.compare_image("model/blocks/clipping_plane.jpeg") == True


def test_blocks_shrink(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["shrink"]["rpc"],
        [
            {
                "ids": [model_id],
                "shrink_factor": 0.8,
            }
        ],
    )
    assert server.compare_image("model/blocks/shrink.jpeg") == True
