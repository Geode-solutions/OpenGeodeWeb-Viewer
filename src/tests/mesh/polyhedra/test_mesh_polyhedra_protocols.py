# Standard library imports
from typing import Callable

# Third party imports
from src.opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from src.opengeodeweb_viewer.rpc.mesh.polyhedra.polyhedra_protocols import (
    VtkMeshPolyhedraView,
)

# Local application imports
from tests.conftest import ServerMonitor


def test_register_mesh(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    dataset_factory(id="123456789", viewable_file_name="polyhedron_attribute.vtu")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "mesh/polyhedra/register.jpeg") == True


def test_polyhedra_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image(3, "mesh/polyhedra/color.jpeg") == True


def test_polyhedra_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image(3, "mesh/polyhedra/visibility.jpeg") == True


def test_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "toto_on_vertices"}],
    )
    assert server.compare_image(3, "mesh/polyhedra/vertex_attribute.jpeg") == True


def test_polyhedron_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolyhedraView.mesh_polyhedra_prefix
        + VtkMeshPolyhedraView.mesh_polyhedra_schemas_dict["polyhedron_attribute"][
            "rpc"
        ],
        [{"id": "123456789", "name": "toto_on_polyhedra"}],
    )
    assert server.compare_image(3, "mesh/polyhedra/polyhedron_attribute.jpeg") == True
