# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.edges.edges_protocols import VtkMeshEdgesView
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView

# Local application imports
from tests.mesh.test_mesh_protocols import test_register_mesh
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "12345678901234567890123456789012"


def test_edges_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": True}],
    )
    assert server.compare_image("mesh/edges/visibility.jpeg") == True


def test_edges_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_edges_visibility(server, dataset_factory)

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["color"]["rpc"],
        [
            {
                "id": mesh_id,
                "color": {"red": 255, "green": 0, "blue": 0, "alpha": 0.5},
            }
        ],
    )
    assert server.compare_image("mesh/edges/color.jpeg") == True


def test_edges_with_edged_curve(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    dataset_factory(
        id=mesh_id, viewable_file="edged_curve.vtp", viewer_elements_type="edges"
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "name": "edged_curve.vtp"}],
    )
    assert server.compare_image("mesh/edges/register_edged_curve.jpeg") == True

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["color"]["rpc"],
        [{"id": mesh_id, "color": {"red": 255, "green": 0, "blue": 0, "alpha": 1}}],
    )
    assert server.compare_image("mesh/edges/edged_curve_color.jpeg") == True

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": False}],
    )
    assert server.compare_image("mesh/edges/edged_curve_visibility.jpeg") == True


def test_edges_clipping_plane(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["clipping_planes"]["rpc"],
        [
            {
                "ids": [mesh_id],
                "planes": [
                    {
                        "origin": [0.0, 2.5, 0.0],
                        "normal": [1.0, 0.0, 1.0],
                    }
                ],
            }
        ],
    )
    assert server.compare_image("mesh/edges/clipping_plane.jpeg") == True


def test_edges_shrink(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["shrink"]["rpc"],
        [
            {
                "ids": [mesh_id],
                "shrink_factor": 0.8,
            }
        ],
    )
    assert server.compare_image("mesh/edges/shrink.jpeg") == True
