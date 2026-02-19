# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.polygons.attribute.vertex.polygons_attribute_vertex_protocols import (
    VtkMeshPolygonsAttributeVertexView,
)

# Local application imports
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "123456789"


def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(
        id=mesh_id, viewable_file="hat.vtp", viewer_elements_type="polygons"
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )


def test_polygons_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "lambert2SG"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
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
                    1.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
    )

    assert server.compare_image("mesh/polygons/vertex_color_map.jpeg") == True


def test_polygons_vertex_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "lambert2SG"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
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
                    1.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
    )

    assert server.compare_image("mesh/polygons/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
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
        server.compare_image("mesh/polygons/vertex_color_map_range_update.jpeg") == True
    )


def test_polygons_vertex_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "lambert2SG"}],
    )

    # Set Blue to Red Map on [0, 1]
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
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
                    1.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
    )

    assert server.compare_image("mesh/polygons/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
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
                    0.1,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 0.1,
            }
        ],
    )

    assert server.compare_image("mesh/polygons/vertex_color_map_red_shift.jpeg") == True


def test_polygons_vertex_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "lambert2SG"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
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
                "maximum": 1.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/polygons/vertex_color_map_rainbow_initial.jpeg")
        == True
    )

    # Update rainbow range via color map
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
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

    assert server.compare_image("mesh/polygons/vertex_color_map_rainbow.jpeg") == True
