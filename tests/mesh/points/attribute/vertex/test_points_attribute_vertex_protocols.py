# Standard library imports
from collections.abc import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.points.attribute.vertex.points_attribute_vertex_protocols import (
    VtkMeshPointsAttributeVertexView,
)
from opengeodeweb_viewer.rpc.mesh.points.points_protocols import VtkMeshPointsView
from opengeodeweb_viewer.rpc.mesh.polygons.attribute.vertex import (
    polygons_attribute_vertex_protocols,
)

# Local application imports
from tests.conftest import ServerMonitor

VtkMeshPolygonsAttributeVertexView = (
    polygons_attribute_vertex_protocols.VtkMeshPolygonsAttributeVertexView
)

# Local constants
mesh_id = "12345678901234567890123456789012"


def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(
        data_id=mesh_id,
        viewable_file="hat.vtp",
        viewer_elements_type="points",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "name": "hat.vtp"}],
    )


def test_points_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "lambert2SG",
                "item": 0,
                "points": [0.0, 0, 0, 1.0, 1.0, 1.0, 0, 0],
                "minimum": 0.0,
                "maximum": 1.0,
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )
    assert server.compare_image("mesh/points/vertex_color_map.jpeg")


def test_points_vertex_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute, item, range and color map
    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "lambert2SG",
                "item": 0,
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
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/points/vertex_color_map.jpeg")

    # Update range via attribute
    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "lambert2SG",
                "item": 0,
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
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/points/vertex_color_map_range_update.jpeg")


def test_points_vertex_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute, item, range and color map
    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "lambert2SG",
                "item": 0,
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
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/points/vertex_color_map.jpeg")

    # Update range via attribute
    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "lambert2SG",
                "item": 0,
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
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/points/vertex_color_map_red_shift.jpeg")


def test_points_vertex_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Rainbow Desaturated Map
    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "lambert2SG",
                "item": 0,
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
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/points/vertex_color_map_rainbow_initial.jpeg")

    # Update rainbow range via attribute
    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "lambert2SG",
                "item": 0,
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
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/points/vertex_color_map_rainbow.jpeg")


def test_points_vertex_attribute_item(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "points",
                "item": 1,
                "points": [
                    2.0,
                    0,
                    0,
                    1.0,
                    498.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 2.0,
                "maximum": 498.0,
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )
    assert server.compare_image("mesh/points/vertex_attribute_item.jpeg")


def display_points_attribute(
    server: ServerMonitor,
    dataset_factory: Callable[..., str],
    viewable_file: str,
    viewer_elements_type: str,
    attribute: dict[str, object],
) -> None:
    dataset_factory(
        data_id=mesh_id,
        viewable_file=viewable_file,
        viewer_elements_type=viewer_elements_type,
    )
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "name": viewable_file}],
    )
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": True}],
    )
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["size"]["rpc"],
        [{"id": mesh_id, "size": 15}],
    )
    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [{"id": mesh_id, **attribute}],
    )


def test_polygons_points_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    display_points_attribute(
        server,
        dataset_factory,
        "hat.vtp",
        "polygons",
        {
            "name": "lambert2SG",
            "item": 0,
            "points": [0.0, 0, 0, 1.0, 1.0, 1.0, 0, 0],
            "minimum": 0.0,
            "maximum": 1.0,
        },
    )
    assert server.compare_image("mesh/points/polygons_points_vertex_attribute.jpeg")


def test_edges_points_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    display_points_attribute(
        server,
        dataset_factory,
        "attributed_edged_curve.vtp",
        "edges",
        {
            "name": "vertex_attribute",
            "item": 0,
            "points": [0.0, 0, 0, 1.0, 58.0, 1.0, 0, 0],
            "minimum": 0.0,
            "maximum": 58.0,
        },
    )
    assert server.compare_image("mesh/points/edges_points_vertex_attribute.jpeg")


def test_cells_points_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    display_points_attribute(
        server,
        dataset_factory,
        "regular_grid_2d.vti",
        "cells",
        {
            "name": "points",
            "item": 0,
            "points": [2.0, 0, 0, 1.0, 498.0, 1.0, 0, 0],
            "minimum": 2.0,
            "maximum": 498.0,
        },
    )
    assert server.compare_image("mesh/points/cells_points_vertex_attribute.jpeg")


def test_polyhedra_points_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    display_points_attribute(
        server,
        dataset_factory,
        "polyhedron_attribute.vtu",
        "polyhedra",
        {
            "name": "toto_on_vertices",
            "item": 0,
            "points": [1.0, 0, 0, 1.0, 11.0, 1.0, 0, 0],
            "minimum": 1.0,
            "maximum": 11.0,
        },
    )
    assert server.compare_image("mesh/points/polyhedra_points_vertex_attribute.jpeg")


def test_polygons_points_shared_scalar_bar(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    attribute = {
        "id": mesh_id,
        "name": "lambert2SG",
        "item": 0,
        "points": [0.0, 0, 0, 1.0, 1.0, 1.0, 0, 0],
        "minimum": 0.0,
        "maximum": 1.0,
    }
    test_polygons_points_vertex_attribute(server, dataset_factory)

    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
            "attribute"
        ]["rpc"],
        [attribute],
    )
    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [attribute],
    )
    assert server.compare_image("mesh/points/polygons_points_shared_scalar_bar.jpeg")


def test_polygons_points_attribute_then_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_polygons_points_vertex_attribute(server, dataset_factory)
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["color"]["rpc"],
        [{"id": mesh_id, "color": {"red": 255, "green": 0, "blue": 0, "alpha": 1.0}}],
    )
    # Red points, no points scalar bar
    assert server.compare_image("mesh/points/polygons_points_attribute_then_color.jpeg")
