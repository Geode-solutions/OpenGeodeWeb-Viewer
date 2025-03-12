# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.model.corners.points.corners_points_protocols import VtkModelCornersPointsView

# Local application imports
from tests.test_model_protocols import test_register_model

def test_corners_points_visibility(server):

    test_register_model(server)

    server.call(VtkModelCornersPointsView.model_corners_points_prefix + VtkModelCornersPointsView.model_corners_points_schemas_dict["visibility"]["rpc"], [{"id": "123456789", "block_ids": ["0"], "visibility": True}])
    assert server.compare_image(3, "model/corners/points/visibility.jpeg") == True