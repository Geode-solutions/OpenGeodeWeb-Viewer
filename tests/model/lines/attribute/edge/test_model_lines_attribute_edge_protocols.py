# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.model.lines.model_lines_protocols import (
    VtkModelLinesView,
)
from opengeodeweb_viewer.rpc.model.lines.attribute.edge.lines_attribute_edge_protocols import (
    VtkModelLinesAttributeEdgeView,
)

# Local application imports
from tests.model.test_model_protocols import test_register_model_cube
from tests.conftest import ServerMonitor

model_id = "123456789"


def test_lines_edge_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    # Hide all blocks to ensure visibility of lines
    server.call(
        VtkModelLinesView.model_lines_prefix
        + VtkModelLinesView.model_lines_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only lines
    server.call(
        VtkModelLinesView.model_lines_prefix
        + VtkModelLinesView.model_lines_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(14, 35)), "visibility": True}],
    )

    server.call(
        VtkModelLinesAttributeEdgeView.model_lines_attribute_edge_prefix
        + VtkModelLinesAttributeEdgeView.model_lines_attribute_edge_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": model_id, "block_ids": list(range(14, 35)), "name": "edges"}],
    )
    assert server.compare_image("model/lines/attribute.jpeg") == True


def test_lines_edge_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    # Hide all blocks to ensure visibility of lines
    server.call(
        VtkModelLinesView.model_lines_prefix
        + VtkModelLinesView.model_lines_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only lines
    server.call(
        VtkModelLinesView.model_lines_prefix
        + VtkModelLinesView.model_lines_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(14, 35)), "visibility": True}],
    )

    # Set active edge attribute
    server.call(
        VtkModelLinesAttributeEdgeView.model_lines_attribute_edge_prefix
        + VtkModelLinesAttributeEdgeView.model_lines_attribute_edge_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": model_id, "block_ids": list(range(14, 35)), "name": "edges"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkModelLinesAttributeEdgeView.model_lines_attribute_edge_prefix
        + VtkModelLinesAttributeEdgeView.model_lines_attribute_edge_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": list(range(14, 35)),
                "points": [
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
    )

    assert server.compare_image("model/lines/color_map.jpeg") == True
