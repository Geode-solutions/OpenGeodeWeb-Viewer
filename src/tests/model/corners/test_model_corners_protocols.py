# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.model.corners.corners_protocols import (
    VtkModelCornersView,
)

# Local application imports
from src.tests.model.test_model_protocols import test_register_model_cube


def test_corners_points_visibility(server):

    test_register_model_cube(server)

    server.call(
        VtkModelCornersView.model_corners_prefix
        + VtkModelCornersView.model_corners_schemas_dict["visibility"]["rpc"],
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
        VtkModelCornersView.model_corners_prefix
        + VtkModelCornersView.model_corners_schemas_dict["visibility"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(1, 13)),
                "visibility": True,
            }
        ],
    )
    assert server.compare_image(3, "model/corners/visibility.jpeg") == True


def test_corners_points_color(server):

    test_corners_points_visibility(server)

    server.call(
        VtkModelCornersView.model_corners_prefix
        + VtkModelCornersView.model_corners_schemas_dict["color"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(1, 13)),
                "color": {"r": 255, "g": 0, "b": 0},
            }
        ],
    )
    assert server.compare_image(3, "model/corners/color.jpeg") == True
