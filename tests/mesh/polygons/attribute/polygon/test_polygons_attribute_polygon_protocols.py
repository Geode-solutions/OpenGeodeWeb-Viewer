# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.polygons.attribute.polygon.polygons_attribute_polygon_protocols import (
    VtkMeshPolygonsAttributePolygonView,
)

# Local application imports
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "123456789"


def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(
        id=mesh_id,
        viewable_file="triangulated_surface2d.vtp",
        viewer_elements_type="polygons",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )



def test_polygons_polygon_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_prefix
        + VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "triangle_vertices"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_prefix
        + VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    50.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 50.0,
            }
        ],
    )

    assert server.compare_image("mesh/polygons/polygon_color_map.jpeg") == True


def test_polygons_polygon_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_prefix
        + VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "triangle_vertices"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_prefix
        + VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    50.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 50.0,
            }
        ],
    )

    assert server.compare_image("mesh/polygons/polygon_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_prefix
        + VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    40.0,
                    0,
                    0,
                    1.0,
                    45.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 40.0,
                "maximum": 45.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/polygons/polygon_color_map_range_update.jpeg")
        == True
    )


def test_polygons_polygon_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_prefix
        + VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "triangle_vertices"}],
    )

    # Set Blue to Red Map on [0, 50]
    server.call(
        VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_prefix
        + VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    50.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 50.0,
            }
        ],
    )

    assert server.compare_image("mesh/polygons/polygon_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_prefix
        + VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    3.0,
                    0,
                    0,
                    1.0,
                    4.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 3.0,
                "maximum": 4.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/polygons/polygon_color_map_red_shift.jpeg") == True
    )


def test_polygons_polygon_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_prefix
        + VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "triangle_vertices"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_prefix
        + VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    0.143 * 50,
                    0,
                    0,
                    92 / 255,
                    0.285 * 50,
                    0,
                    255 / 255,
                    255 / 255,
                    0.429 * 50,
                    0,
                    128 / 255,
                    0,
                    0.571 * 50,
                    255 / 255,
                    255 / 255,
                    0,
                    0.714 * 50,
                    255 / 255,
                    97 / 255,
                    0,
                    0.857 * 50,
                    107 / 255,
                    0,
                    0,
                    50.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 0.0,
                "maximum": 50.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/polygons/polygon_color_map_rainbow_initial.jpeg")
        == True
    )

    # Update rainbow range via color map
    server.call(
        VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_prefix
        + VtkMeshPolygonsAttributePolygonView.mesh_polygons_attribute_polygon_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    5.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    5.0 + 0.143 * 10,
                    0,
                    0,
                    92 / 255,
                    5.0 + 0.285 * 10,
                    0,
                    255 / 255,
                    255 / 255,
                    5.0 + 0.429 * 10,
                    0,
                    128 / 255,
                    0,
                    5.0 + 0.571 * 10,
                    255 / 255,
                    255 / 255,
                    0,
                    5.0 + 0.714 * 10,
                    255 / 255,
                    97 / 255,
                    0,
                    5.0 + 0.857 * 10,
                    107 / 255,
                    0,
                    0,
                    15.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 5.0,
                "maximum": 15.0,
            }
        ],
    )

    assert server.compare_image("mesh/polygons/polygon_color_map_rainbow.jpeg") == True
