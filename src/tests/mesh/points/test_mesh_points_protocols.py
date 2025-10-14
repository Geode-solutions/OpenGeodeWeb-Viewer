# Standard library imports
from typing import Callable, cast

# Third party imports
from src.opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from src.opengeodeweb_viewer.rpc.mesh.points.mesh_points_protocols import (
    VtkMeshPointsView,
)

# Local application imports
from tests.mesh.test_mesh_protocols import test_register_mesh
from tests.conftest import ServerMonitor


def test_points_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + cast(str, VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"]),
        [{"id": mesh_id, "visibility": True}],
    )
    assert server.compare_image(3, "mesh/points/visibility.jpeg") == True


def test_points_size(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    test_points_visibility(server, dataset_factory)

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + cast(str, VtkMeshPointsView.mesh_points_schemas_dict["size"]["rpc"]),
        [{"id": mesh_id, "size": 15}],
    )
    assert server.compare_image(3, "mesh/points/size.jpeg") == True


def test_points_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    test_points_size(server, dataset_factory)

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + cast(str, VtkMeshPointsView.mesh_points_schemas_dict["color"]["rpc"]),
        [{"id": mesh_id, "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image(3, "mesh/points/color.jpeg") == True


def test_points_with_point_set(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "44556677"

    dataset_factory(id=mesh_id, viewable_file_name="points.vtp")
    server.call(
        VtkMeshView.mesh_prefix
        + cast(str, VtkMeshView.mesh_schemas_dict["register"]["rpc"]),
        [{"id": mesh_id}],
    )
    assert server.compare_image(3, "mesh/points/register_point_set.jpeg") == True

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + cast(str, VtkMeshPointsView.mesh_points_schemas_dict["size"]["rpc"]),
        [{"id": mesh_id, "size": 10}],
    )
    assert server.compare_image(3, "mesh/points/point_set_size.jpeg") == True

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + cast(str, VtkMeshPointsView.mesh_points_schemas_dict["color"]["rpc"]),
        [{"id": mesh_id, "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image(3, "mesh/points/point_set_color.jpeg") == True

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + cast(str, VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"]),
        [{"id": mesh_id, "visibility": False}],
    )
    assert server.compare_image(3, "mesh/points/point_set_visibility.jpeg") == True
