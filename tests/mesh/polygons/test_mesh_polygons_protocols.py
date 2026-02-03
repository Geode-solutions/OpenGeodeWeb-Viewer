# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.polygons.polygons_protocols import VtkMeshPolygonsView

# Local application imports
from tests.mesh.test_mesh_protocols import test_register_mesh
from tests.conftest import ServerMonitor


def test_polygons_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("mesh/polygons/color.jpeg") == True


def test_polygons_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image("mesh/polygons/visibility.jpeg") == True


def test_polygons_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "lambert2SG"}],
    )
    assert server.compare_image("mesh/polygons/vertex_attribute.jpeg") == True

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": "123456789", "minimum": 0, "maximum": 10}],
    )
    assert server.compare_image("mesh/polygons/vertex_scalar_range.jpeg") == True


def test_polygons_polygon_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    dataset_factory(
        id="123456789",
        viewable_file="triangulated_surface2d.vtp",
        viewer_elements_type="polygons",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image("mesh/polygons/register.jpeg") == True

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_attribute"]["rpc"],
        [{"id": "123456789", "name": "triangle_vertices"}],
    )
    assert server.compare_image("mesh/polygons/polygon_attribute.jpeg") == True

    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_scalar_range"]["rpc"],
        [{"id": "123456789", "minimum": 0, "maximum": 10}],
    )
    assert server.compare_image("mesh/polygons/polygon_scalar_range.jpeg") == True


def test_polygons_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "lambert2SG"}],
    )

    # Set scalar range
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": "123456789", "minimum": 0, "maximum": 1}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polygons/vertex_color_map.jpeg") == True


def test_polygons_vertex_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "lambert2SG"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polygons/vertex_color_map.jpeg") == True

    # Set scalar range: 0.8 to 1 (clamping data to the minimum color -> mostly BLUE)
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": "123456789", "minimum": 0.8, "maximum": 1.0}],
    )

    assert (
        server.compare_image("mesh/polygons/vertex_color_map_range_update.jpeg") == True
    )


def test_polygons_vertex_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "lambert2SG"}],
    )

    # Set Blue to Red Map on [0, 1]
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polygons/vertex_color_map.jpeg") == True

    # Set scalar range: 0.0 to 0.1 (all data > 0.1 should become RED)
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": "123456789", "minimum": 0.0, "maximum": 0.1}],
    )

    assert server.compare_image("mesh/polygons/vertex_color_map_red_shift.jpeg") == True


def test_polygons_vertex_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "lambert2SG"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": "123456789",
                "points": [
                    [0.0, 71, 71, 219],
                    [0.143, 0, 0, 92],
                    [0.285, 0, 255, 255],
                    [0.429, 0, 128, 0],
                    [0.571, 255, 255, 0],
                    [0.714, 255, 97, 0],
                    [0.857, 107, 0, 0],
                    [1.0, 224, 77, 77],
                ],
            }
        ],
    )

    assert (
        server.compare_image("mesh/polygons/vertex_color_map_rainbow_initial.jpeg")
        == True
    )

    # Set scalar range: 0.1 to 0.4
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": "123456789", "minimum": 0.1, "maximum": 0.4}],
    )

    assert server.compare_image("mesh/polygons/vertex_color_map_rainbow.jpeg") == True


def test_polygons_polygon_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    dataset_factory(
        id=mesh_id,
        viewable_file="triangulated_surface2d.vtp",
        viewer_elements_type="polygons",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )

    # Set active attribute
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_attribute"]["rpc"],
        [{"id": mesh_id, "name": "triangle_vertices"}],
    )

    # Set scalar range
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 0, "maximum": 50}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polygons/polygon_color_map.jpeg") == True


def test_polygons_polygon_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    dataset_factory(
        id=mesh_id,
        viewable_file="triangulated_surface2d.vtp",
        viewer_elements_type="polygons",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )

    # Set active attribute
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_attribute"]["rpc"],
        [{"id": mesh_id, "name": "triangle_vertices"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polygons/polygon_color_map.jpeg") == True

    # Set scalar range: 40 to 45 (clamping data to the minimum color -> mostly BLUE)
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 40.0, "maximum": 45.0}],
    )

    assert (
        server.compare_image("mesh/polygons/polygon_color_map_range_update.jpeg")
        == True
    )


def test_polygons_polygon_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    dataset_factory(
        id=mesh_id,
        viewable_file="triangulated_surface2d.vtp",
        viewer_elements_type="polygons",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )

    # Set active attribute
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_attribute"]["rpc"],
        [{"id": mesh_id, "name": "triangle_vertices"}],
    )

    # Set Blue to Red Map on [0, 1]
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    [0.0, 0, 0, 255],
                    [1.0, 255, 0, 0],
                ],
            }
        ],
    )

    assert server.compare_image("mesh/polygons/polygon_color_map.jpeg") == True

    # Set scalar range: 3.0 to 4.0 (all data > 4 should become RED)
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 3.0, "maximum": 4.0}],
    )

    assert (
        server.compare_image("mesh/polygons/polygon_color_map_red_shift.jpeg") == True
    )


def test_polygons_polygon_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    mesh_id = "123456789"
    dataset_factory(
        id=mesh_id,
        viewable_file="triangulated_surface2d.vtp",
        viewer_elements_type="polygons",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )

    # Set active attribute
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_attribute"]["rpc"],
        [{"id": mesh_id, "name": "triangle_vertices"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    [0.0, 71, 71, 219],
                    [0.143, 0, 0, 92],
                    [0.285, 0, 255, 255],
                    [0.429, 0, 128, 0],
                    [0.571, 255, 255, 0],
                    [0.714, 255, 97, 0],
                    [0.857, 107, 0, 0],
                    [1.0, 224, 77, 77],
                ],
            }
        ],
    )

    assert (
        server.compare_image("mesh/polygons/polygon_color_map_rainbow_initial.jpeg")
        == True
    )

    # Set scalar range: 5.0 to 15.0
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["polygon_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 5.0, "maximum": 15.0}],
    )

    assert server.compare_image("mesh/polygons/polygon_color_map_rainbow.jpeg") == True
