# Standard library imports

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.points.mesh_points_protocols import VtkMeshPointsView

# Local application imports
# from src.tests.test_data_helpers import create_mesh_data

def test_points_visibility(server):
    mesh_id = "123456789"
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )
    server.compare_image(3, "mesh/register.jpeg")
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": True}],
    )
    assert server.compare_image(3, "mesh/points/visibility.jpeg") == True


def test_points_size(server):
    mesh_id = "123456789"
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )
    server.compare_image(3, "mesh/register.jpeg")
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": True}],
    )
    server.compare_image(3, "mesh/points/visibility.jpeg")
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["size"]["rpc"],
        [{"id": mesh_id, "size": 15}],
    )
    assert server.compare_image(3, "mesh/points/size.jpeg") == True


def test_points_color(server):
    mesh_id = "123456789"

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )
    server.compare_image(3, "mesh/register.jpeg")
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": True}],
    )
    server.compare_image(3, "mesh/points/visibility.jpeg")
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["size"]["rpc"],
        [{"id": mesh_id, "size": 15}],
    )
    server.compare_image(3, "mesh/points/size.jpeg")
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["color"]["rpc"],
        [{"id": mesh_id, "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image(3, "mesh/points/color.jpeg") == True


def test_points_with_point_set(server):
    mesh_id = "44556677"
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )
    assert server.compare_image(3, "mesh/points/register_point_set.jpeg") == True
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["size"]["rpc"],
        [{"id": mesh_id, "size": 10}],
    )
    assert server.compare_image(3, "mesh/points/point_set_size.jpeg") == True
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["color"]["rpc"],
        [{"id": mesh_id, "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image(3, "mesh/points/point_set_color.jpeg") == True
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": False}],
    )
    assert server.compare_image(3, "mesh/points/point_set_visibility.jpeg") == True
