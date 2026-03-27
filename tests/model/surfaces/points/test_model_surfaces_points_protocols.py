# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.model.surfaces.points.model_surfaces_points_protocols import (
    VtkModelSurfacesPointsView,
)

# Local application imports
from tests.model.test_model_protocols import test_register_model_cube
from tests.conftest import ServerMonitor


def test_surfaces_points_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_model_cube(server, dataset_factory)

    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["visibility"][
            "rpc"
        ],
        [{"id": "123456789", "visibility": True}],
    )
    assert server.compare_image("model/surfaces/points/visibility_true.jpeg") == True

    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["visibility"][
            "rpc"
        ],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image("model/surfaces/points/visibility_false.jpeg") == True


def test_surfaces_points_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_surfaces_points_visibility(server, dataset_factory)

    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["visibility"][
            "rpc"
        ],
        [{"id": "123456789", "visibility": True}],
    )

    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 0, "g": 0, "b": 255}}],
    )
    assert server.compare_image("model/surfaces/points/color.jpeg") == True


def test_surfaces_points_size(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_surfaces_points_visibility(server, dataset_factory)

    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["visibility"][
            "rpc"
        ],
        [{"id": "123456789", "visibility": True}],
    )

    server.call(
        VtkModelSurfacesPointsView.model_surfaces_points_prefix
        + VtkModelSurfacesPointsView.model_surfaces_points_schemas_dict["size"]["rpc"],
        [{"id": "123456789", "size": 8.0}],
    )
    assert server.compare_image("model/surfaces/points/size.jpeg") == True
