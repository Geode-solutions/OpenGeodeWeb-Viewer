# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.model.blocks.model_blocks_protocols import (
    VtkModelBlocksView,
)
from opengeodeweb_viewer.rpc.model.blocks.attribute.polyhedron.blocks_attribute_polyhedron_protocols import (
    VtkModelBlocksAttributePolyhedronView,
)

# Local application imports
from tests.model.test_model_protocols import test_register_model_cube
from tests.conftest import ServerMonitor

model_id = "123456789"


def test_blocks_polyhedron_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    # Hide all blocks to ensure visibility of blocks
    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only blocks
    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(48, 50)), "visibility": True}],
    )

    server.call(
        VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_prefix
        + VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": model_id, "block_ids": list(range(48, 50)), "name": "tetrahedron_vertices"}],
    )
    assert (
        server.compare_image("model/blocks/attribute.jpeg") == True
    )


def test_blocks_polyhedron_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    # Hide all blocks to ensure visibility of blocks
    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only blocks
    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(48, 50)), "visibility": True}],
    )

    # Set active polyhedron attribute
    server.call(
        VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_prefix
        + VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": model_id, "block_ids": list(range(48, 50)), "name": "tetrahedron_vertices"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_prefix
        + VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": list(range(48, 50)),
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
        server.compare_image("model/blocks/polyhedron_color_map.jpeg") == True
    )
