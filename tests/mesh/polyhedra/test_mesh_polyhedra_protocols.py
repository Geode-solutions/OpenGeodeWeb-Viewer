# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.polyhedra.polyhedra_protocols import (
    VtkMeshPolyhedraView,
)
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView

# Local application imports
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "12345678901234567890123456789012"


def test_register_mesh(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    dataset_factory(
        id=mesh_id,
        viewable_file="polyhedron_attribute.vtu",
        viewer_elements_type="polyhedra",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "name": "polyhedron_attribute.vtu"}],
    )
    assert server.compare_image("mesh/polyhedra/register.jpeg") == True


def test_polyhedra_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["color"]["rpc"],
        [
            {
                "id": mesh_id,
                "color": {"red": 255, "green": 0, "blue": 0, "alpha": 1.0},
            }
        ],
    )
    assert server.compare_image("mesh/polyhedra/color.jpeg") == True


def test_polyhedra_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": False}],
    )
    assert server.compare_image("mesh/polyhedra/visibility.jpeg") == True


def test_polyhedra_clipping_plane(
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
                        "origin": [0.5, 0.5, 0.5],
                        "normal": [-1.0, 0.0, 0.0],
                    }
                ],
            }
        ],
    )
    assert server.compare_image("mesh/polyhedra/clipping_plane.jpeg") == True
