# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.edges.mesh_edges_protocols import VtkMeshEdgesView

# Local application imports
from tests.mesh.test_mesh_protocols import test_register_mesh
from tests.conftest import ServerMonitor


def test_edges_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": True}],
    )
    assert server.compare_image("mesh/edges/visibility.jpeg") == True


def test_edges_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_edges_visibility(server, dataset_factory)

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("mesh/edges/color.jpeg") == True


def test_edges_with_edged_curve(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    dataset_factory(id="123456789", viewable_file="edged_curve.vtp")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image("mesh/edges/register_edged_curve.jpeg") == True

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("mesh/edges/edged_curve_color.jpeg") == True

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image("mesh/edges/edged_curve_visibility.jpeg") == True


def test_edges_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    dataset_factory(id=mesh_id, viewable_file="attributed_edged_curve.vtp")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "vertex_attribute"}],
    )
    assert server.compare_image("mesh/edges/vertex_attribute.jpeg") == True

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 0, "maximum": 10}],
    )
    assert server.compare_image("mesh/edges/vertex_scalar_range.jpeg") == True
