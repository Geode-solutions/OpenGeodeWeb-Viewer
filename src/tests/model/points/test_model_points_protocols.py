# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.model.points.model_points_protocols import (
    VtkModelPointsView,
)

# Local application imports
from src.tests.model.test_model_protocols import test_register_model


def test_points_visibility(server):

    test_register_model(server)

    server.call(
        VtkModelPointsView.model_points_prefix
        + VtkModelPointsView.model_points_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": True}],
    )
    assert server.compare_image(3, "model/points/visibility.jpeg") == True


def test_points_size(server):

    test_points_visibility(server)

    server.call(
        VtkModelPointsView.model_points_prefix
        + VtkModelPointsView.model_points_schemas_dict["size"]["rpc"],
        [{"id": "123456789", "size": 20}],
    )
    assert server.compare_image(3, "model/points/size.jpeg") == True
