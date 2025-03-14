# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.rpc.model.corners.points.corners_points_protocols import VtkModelCornersPointsView

# Local application imports


def test_register_model(server):

    server.call(VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"], [{"id": "123456789", "file_name": "cube.vtm"}])
    assert server.compare_image(3, "model/cube_register.jpeg") == True


def test_corners_points_visibility(server):

    test_register_model(server)

    server.call(VtkModelCornersPointsView.model_corners_points_prefix + VtkModelCornersPointsView.model_corners_points_schemas_dict["visibility"]["rpc"], [{"id": "123456789", "block_ids": ["0"], "visibility": True}])
    assert server.compare_image(3, "model/corners/points/visibility.jpeg") == True