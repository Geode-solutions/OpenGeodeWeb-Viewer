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
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(48, 50)),
                "name": "tetrahedron_vertices",
                "item": 0,
                "points": [
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
    )
    assert server.compare_image("model/blocks/attribute.jpeg") == True


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

    # Set active polyhedron attribute, item, color map & range
    server.call(
        VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_prefix
        + VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(48, 50)),
                "name": "tetrahedron_vertices",
                "item": 0,
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

    assert server.compare_image("model/blocks/color_map.jpeg") == True


def test_blocks_polyhedron_color_map_range_update(
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
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(48, 50)),
                "name": "tetrahedron_vertices",
                "item": 0,
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

    assert server.compare_image("model/blocks/color_map.jpeg") == True

    # Update range via attribute
    server.call(
        VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_prefix
        + VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(48, 50)),
                "name": "tetrahedron_vertices",
                "item": 0,
                "points": [
                    40.0,
                    0.0,
                    0.0,
                    1.0,
                    45.0,
                    1.0,
                    0.0,
                    0.0,
                ],
                "minimum": 40.0,
                "maximum": 45.0,
            }
        ],
    )

    assert server.compare_image("model/blocks/updated_color_map.jpeg") == True


def test_blocks_polyhedron_color_map_red_shift(
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
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(48, 50)),
                "name": "tetrahedron_vertices",
                "item": 0,
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

    assert server.compare_image("model/blocks/color_map.jpeg") == True

    # Update range via attribute
    server.call(
        VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_prefix
        + VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(48, 50)),
                "name": "tetrahedron_vertices",
                "item": 0,
                "points": [
                    3.0,
                    0.0,
                    0.0,
                    1.0,
                    4.0,
                    1.0,
                    0.0,
                    0.0,
                ],
                "minimum": 3.0,
                "maximum": 4.0,
            }
        ],
    )

    assert server.compare_image("model/blocks/color_map_red_shift.jpeg") == True


def test_blocks_polyhedron_color_map_rainbow(
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

    # Rainbow Desaturated Map
    server.call(
        VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_prefix
        + VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(48, 50)),
                "name": "tetrahedron_vertices",
                "item": 0,
                "points": [
                    0.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    0.143 * 50,
                    0,
                    0,
                    92 / 255,
                    0.285 * 50,
                    0,
                    255 / 255,
                    255 / 255,
                    0.429 * 50,
                    0,
                    128 / 255,
                    0,
                    0.571 * 50,
                    255 / 255,
                    255 / 255,
                    0,
                    0.714 * 50,
                    255 / 255,
                    97 / 255,
                    0,
                    0.857 * 50,
                    107 / 255,
                    0,
                    0,
                    50.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 0.0,
                "maximum": 50.0,
            }
        ],
    )

    assert server.compare_image("model/blocks/color_map_rainbow_initial.jpeg") == True

    # Update rainbow range via attribute
    server.call(
        VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_prefix
        + VtkModelBlocksAttributePolyhedronView.model_blocks_attribute_polyhedron_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(48, 50)),
                "name": "tetrahedron_vertices",
                "item": 0,
                "points": [
                    5.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    5.0 + 0.143 * 10,
                    0,
                    0,
                    92 / 255,
                    5.0 + 0.285 * 10,
                    0,
                    255 / 255,
                    255 / 255,
                    5.0 + 0.429 * 10,
                    0,
                    128 / 255,
                    0,
                    5.0 + 0.571 * 10,
                    255 / 255,
                    255 / 255,
                    0,
                    5.0 + 0.714 * 10,
                    255 / 255,
                    97 / 255,
                    0,
                    5.0 + 0.857 * 10,
                    107 / 255,
                    0,
                    0,
                    15.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 5.0,
                "maximum": 15.0,
            }
        ],
    )

    assert server.compare_image("model/blocks/color_map_rainbow.jpeg") == True
