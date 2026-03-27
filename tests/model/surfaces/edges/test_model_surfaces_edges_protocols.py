# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.model.surfaces.edges.model_surfaces_edges_protocols import (
    VtkModelSurfacesEdgesView,
)

# Local application imports
from tests.model.test_model_protocols import test_register_model_cube
from tests.conftest import ServerMonitor


def test_surfaces_edges_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_model_cube(server, dataset_factory)

    server.call(
        VtkModelSurfacesEdgesView.model_surfaces_edges_prefix
        + VtkModelSurfacesEdgesView.model_surfaces_edges_schemas_dict["visibility"][
            "rpc"
        ],
        [{"id": "123456789", "visibility": True}],
    )
    assert server.compare_image("model/surfaces/edges/visibility_true.jpeg") == True

    server.call(
        VtkModelSurfacesEdgesView.model_surfaces_edges_prefix
        + VtkModelSurfacesEdgesView.model_surfaces_edges_schemas_dict["visibility"][
            "rpc"
        ],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image("model/surfaces/edges/visibility_false.jpeg") == True


def test_surfaces_edges_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_model_cube(server, dataset_factory)

    # Activer les edges d'abord
    server.call(
        VtkModelSurfacesEdgesView.model_surfaces_edges_prefix
        + VtkModelSurfacesEdgesView.model_surfaces_edges_schemas_dict["visibility"][
            "rpc"
        ],
        [{"id": "123456789", "visibility": True}],
    )
    # Puis changer la couleur
    server.call(
        VtkModelSurfacesEdgesView.model_surfaces_edges_prefix
        + VtkModelSurfacesEdgesView.model_surfaces_edges_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("model/surfaces/edges/color.jpeg") == True


def test_surfaces_edges_width(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_surfaces_edges_visibility(server, dataset_factory)

    server.call(
        VtkModelSurfacesEdgesView.model_surfaces_edges_prefix
        + VtkModelSurfacesEdgesView.model_surfaces_edges_schemas_dict["visibility"][
            "rpc"
        ],
        [{"id": "123456789", "visibility": True}],
    )

    server.call(
        VtkModelSurfacesEdgesView.model_surfaces_edges_prefix
        + VtkModelSurfacesEdgesView.model_surfaces_edges_schemas_dict["width"]["rpc"],
        [{"id": "123456789", "width": 5.0}],
    )
    assert server.compare_image("model/surfaces/edges/width.jpeg") == True
