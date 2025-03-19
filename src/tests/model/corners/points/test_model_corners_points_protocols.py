# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.model.corners.points.corners_points_protocols import (
    VtkModelCornersPointsView,
)

# Local application imports
from src.tests.model.test_model_protocols import test_register_model_cube


def test_corners_points_visibility(server):

    test_register_model_cube(server)

    server.call(
        VtkModelCornersPointsView.model_corners_points_prefix
        + VtkModelCornersPointsView.model_corners_points_schemas_dict["visibility"][
            "rpc"
        ],
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
        VtkModelCornersPointsView.model_corners_points_prefix
        + VtkModelCornersPointsView.model_corners_points_schemas_dict["visibility"][
            "rpc"
        ],
        [
            {
                "id": "123456789",
                "block_ids": list(range(1, 13)),
                "visibility": True,
            }
        ],
    )
    assert server.compare_image(3, "model/corners/points/visibility.jpeg") == True


def test_corners_points_color(server):

    test_corners_points_visibility(server)

    server.call(
        VtkModelCornersPointsView.model_corners_points_prefix
        + VtkModelCornersPointsView.model_corners_points_schemas_dict["color"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": list(range(1, 13)),
                "color": {"r": 255, "g": 0, "b": 0},
            }
        ],
    )
    assert server.compare_image(3, "model/corners/points/color.jpeg") == True
