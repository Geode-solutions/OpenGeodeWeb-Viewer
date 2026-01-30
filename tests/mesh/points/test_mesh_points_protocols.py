# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.points.mesh_points_protocols import (
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
        + VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": True}],
    )
    assert server.compare_image("mesh/points/visibility.jpeg") == True


def test_points_size(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    test_points_visibility(server, dataset_factory)

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["size"]["rpc"],
        [{"id": mesh_id, "size": 15}],
    )
    assert server.compare_image("mesh/points/size.jpeg") == True


def test_points_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    test_points_size(server, dataset_factory)

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["color"]["rpc"],
        [{"id": mesh_id, "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("mesh/points/color.jpeg") == True


def test_points_with_point_set(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "44556677"

    dataset_factory(id=mesh_id, viewable_file="points.vtp")
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )
    assert server.compare_image("mesh/points/register_point_set.jpeg") == True

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["size"]["rpc"],
        [{"id": mesh_id, "size": 10}],
    )
    assert server.compare_image("mesh/points/point_set_size.jpeg") == True

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["color"]["rpc"],
        [{"id": mesh_id, "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("mesh/points/point_set_color.jpeg") == True

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": False}],
    )
    assert server.compare_image("mesh/points/point_set_visibility.jpeg") == True


def test_points_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "lambert2SG"}],
    )
    assert server.compare_image("mesh/points/vertex_attribute.jpeg") == True


def test_points_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "lambert2SG"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    1.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
            }
        ],
    )

    assert server.compare_image("mesh/points/vertex_color_map.jpeg") == True


def test_points_vertex_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "lambert2SG"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    1.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
            }
        ],
    )

    assert server.compare_image("mesh/points/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    0.8,
                    0,
                    0,
                    1.0,
                    1.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.8,
                "maximum": 1.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/points/vertex_color_map_range_update.jpeg") == True
    )


def test_points_vertex_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "lambert2SG"}],
    )

    # Set Blue to Red Map on [0, 1]
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    1.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
            }
        ],
    )

    assert server.compare_image("mesh/points/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    0.1,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
            }
        ],
    )

    assert server.compare_image("mesh/points/vertex_color_map_red_shift.jpeg") == True


def test_points_vertex_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "lambert2SG"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    0.143,
                    0,
                    0,
                    92 / 255,
                    0.285,
                    0,
                    255 / 255,
                    255 / 255,
                    0.429,
                    0,
                    128 / 255,
                    0,
                    0.571,
                    255 / 255,
                    255 / 255,
                    0,
                    0.714,
                    255 / 255,
                    97 / 255,
                    0,
                    0.857,
                    107 / 255,
                    0,
                    0,
                    1.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/points/vertex_color_map_rainbow_initial.jpeg")
        == True
    )

    # Update rainbow range via color map
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    0.1,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    0.1 + 0.143 * 0.3,
                    0,
                    0,
                    92 / 255,
                    0.1 + 0.285 * 0.3,
                    0,
                    255 / 255,
                    255 / 255,
                    0.1 + 0.429 * 0.3,
                    0,
                    128 / 255,
                    0,
                    0.1 + 0.571 * 0.3,
                    255 / 255,
                    255 / 255,
                    0,
                    0.1 + 0.714 * 0.3,
                    255 / 255,
                    97 / 255,
                    0,
                    0.1 + 0.857 * 0.3,
                    107 / 255,
                    0,
                    0,
                    0.4,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 0.1,
                "maximum": 0.4,
            }
        ],
    )

    assert server.compare_image("mesh/points/vertex_color_map_rainbow.jpeg") == True
