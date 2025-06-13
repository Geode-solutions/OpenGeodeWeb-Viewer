# Standard library imports

# Third party imports
from src.opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from src.opengeodeweb_viewer.rpc.mesh.edges.mesh_edges_protocols import VtkMeshEdgesView

# Local application imports
from src.tests.mesh.test_mesh_protocols import test_register_mesh


def test_edges_visibility(server):

    test_register_mesh(server)

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": True}],
    )
    assert server.compare_image(3, "mesh/edges/visibility.jpeg") == True


def test_edges_color(server):

    test_edges_visibility(server)

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image(3, "mesh/edges/color.jpeg") == True


def test_edges_with_edged_curve(server):

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789", "file_name": "edged_curve.vtp"}],
    )
    assert server.compare_image(3, "mesh/edges/register_edged_curve.jpeg") == True

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image(3, "mesh/edges/edged_curve_color.jpeg") == True

    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image(3, "mesh/edges/edged_curve_visibility.jpeg") == True
