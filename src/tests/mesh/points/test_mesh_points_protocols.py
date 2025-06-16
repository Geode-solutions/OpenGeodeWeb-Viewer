# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.points.mesh_points_protocols import VtkMeshPointsView

# Local application imports
from src.tests.mesh.test_mesh_protocols import test_register_mesh


def test_points_visibility(server):

    test_register_mesh(server)

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": True}],
    )
    assert server.compare_image(3, "mesh/points/visibility.jpeg") == True


def test_points_size(server):

    test_points_visibility(server)

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["size"]["rpc"],
        [{"id": "123456789", "size": 15}],
    )
    assert server.compare_image(3, "mesh/points/size.jpeg") == True


def test_points_color(server):

    test_points_size(server)

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image(3, "mesh/points/color.jpeg") == True


def test_points_with_point_set(server):

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789", "file_name": "points.vtp"}],
    )
    assert server.compare_image(3, "mesh/points/register_point_set.jpeg") == True

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["size"]["rpc"],
        [{"id": "123456789", "size": 10}],
    )
    assert server.compare_image(3, "mesh/points/point_set_size.jpeg") == True

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image(3, "mesh/points/point_set_color.jpeg") == True

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image(3, "mesh/points/point_set_visibility.jpeg") == True
