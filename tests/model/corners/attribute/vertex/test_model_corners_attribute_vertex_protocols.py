# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.model.corners.model_corners_protocols import (
    VtkModelCornersView,
)
from opengeodeweb_viewer.rpc.model.corners.attribute.vertex.corners_attribute_vertex_protocols import (
    VtkModelCornersAttributeVertexView,
)

# Local application imports
from tests.model.test_model_protocols import test_register_model_cube
from tests.conftest import ServerMonitor

model_id = "123456789"


def test_corners_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    # Hide all blocks to ensure visibility of corners
    server.call(
        VtkModelCornersView.model_corners_prefix
        + VtkModelCornersView.model_corners_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only corners
    server.call(
        VtkModelCornersView.model_corners_prefix
        + VtkModelCornersView.model_corners_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 13)), "visibility": True}],
    )

    # Set active vertex attribute
    server.call(
        VtkModelCornersAttributeVertexView.model_corners_attribute_vertex_prefix
        + VtkModelCornersAttributeVertexView.model_corners_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 13)), "name": "unique vertices"}],
    )
    assert (
        server.compare_image("model/corners/attribute/vertex/attribute.jpeg") == True
    )


def test_corners_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    # Hide all blocks to ensure visibility of corners
    server.call(
        VtkModelCornersView.model_corners_prefix
        + VtkModelCornersView.model_corners_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only corners
    server.call(
        VtkModelCornersView.model_corners_prefix
        + VtkModelCornersView.model_corners_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 13)), "visibility": True}],
    )

    # Set active vertex attribute
    server.call(
        VtkModelCornersAttributeVertexView.model_corners_attribute_vertex_prefix
        + VtkModelCornersAttributeVertexView.model_corners_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 13)), "name": "unique vertices"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkModelCornersAttributeVertexView.model_corners_attribute_vertex_prefix
        + VtkModelCornersAttributeVertexView.model_corners_attribute_vertex_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": list(range(1, 13)),
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

    assert (
        server.compare_image("model/corners/color_map.jpeg") == True
    )
