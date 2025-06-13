# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.model.blocks.model_blocks_protocols import (
    VtkModelBlocksView,
)

# Local application imports
from src.tests.model.test_model_protocols import test_register_model_cube


def test_blocks_polyhedra_visibility(server):

    test_register_model_cube(server)

    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["visibility"]["rpc"],
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
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["visibility"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(48, 50)),
                "visibility": True,
            }
        ],
    )

    assert server.compare_image(3, "model/blocks/visibility.jpeg") == True


def test_blocks_polyhedra_color(server):

    test_blocks_polyhedra_visibility(server)

    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["color"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(48, 50)),
                "color": {"r": 255, "g": 0, "b": 0},
            }
        ],
    )
    assert server.compare_image(3, "model/blocks/color.jpeg") == True
