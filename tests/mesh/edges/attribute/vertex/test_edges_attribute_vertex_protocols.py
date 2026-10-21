# Standard library imports

from typing import TYPE_CHECKING

from opengeodeweb_viewer.rpc.mesh.edges.attribute.vertex.edges_attribute_vertex_protocols import (
    VtkMeshEdgesAttributeVertexView,
)
from opengeodeweb_viewer.rpc.mesh.edges.edges_protocols import VtkMeshEdgesView

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.points.attribute.vertex.points_attribute_vertex_protocols import (
    VtkMeshPointsAttributeVertexView,
)
from opengeodeweb_viewer.rpc.mesh.points.points_protocols import VtkMeshPointsView
from opengeodeweb_viewer.rpc.mesh.polygons.attribute.vertex import (
    polygons_attribute_vertex_protocols,
)
from opengeodeweb_viewer.rpc.mesh.polygons.polygons_protocols import VtkMeshPolygonsView

# Local application imports

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.conftest import ServerMonitor

VtkMeshPolygonsAttributeVertexView = (
    polygons_attribute_vertex_protocols.VtkMeshPolygonsAttributeVertexView
)

# Local constants
mesh_id = "12345678901234567890123456789012"


def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(
        data_id=mesh_id,
        viewable_file="attributed_edged_curve.vtp",
        viewer_elements_type="edges",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "name": "attributed_edged_curve.vtp"}],
    )


def test_edges_vertex_color_map(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_register(server, dataset_factory)

    # Set active attribute, item, range and color map
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "vertex_attribute",
                "item": 0,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    58.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map.jpeg")


def test_edges_vertex_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute, item, range and color map
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "vertex_attribute",
                "item": 0,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    58.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map.jpeg")

    # Update range via attribute
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "vertex_attribute",
                "item": 0,
                "points": [
                    50.0,
                    0,
                    0,
                    1.0,
                    58.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 50.0,
                "maximum": 58.0,
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map_range_update.jpeg")


def test_edges_vertex_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute, item, range and color map
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "vertex_attribute",
                "item": 0,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    58.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map.jpeg")

    # Update range via attribute
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "vertex_attribute",
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

    assert server.compare_image("mesh/edges/vertex_color_map_red_shift.jpeg")


def test_edges_vertex_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Rainbow Desaturated Map
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "vertex_attribute",
                "item": 0,
                "points": [
                    0.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    0.143 * 58,
                    0,
                    0,
                    92 / 255,
                    0.285 * 58,
                    0,
                    255 / 255,
                    255 / 255,
                    0.429 * 58,
                    0,
                    128 / 255,
                    0,
                    0.571 * 58,
                    255 / 255,
                    255 / 255,
                    0,
                    0.714 * 58,
                    255 / 255,
                    97 / 255,
                    0,
                    0.857 * 58,
                    107 / 255,
                    0,
                    0,
                    58.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map_rainbow_initial.jpeg")

    # Update rainbow range via attribute
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "vertex_attribute",
                "item": 0,
                "points": [
                    10.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    10.0 + 0.143 * 10,
                    0,
                    0,
                    92 / 255,
                    10.0 + 0.285 * 10,
                    0,
                    255 / 255,
                    255 / 255,
                    10.0 + 0.429 * 10,
                    0,
                    128 / 255,
                    0,
                    10.0 + 0.571 * 10,
                    255 / 255,
                    255 / 255,
                    0,
                    10.0 + 0.714 * 10,
                    255 / 255,
                    97 / 255,
                    0,
                    10.0 + 0.857 * 10,
                    107 / 255,
                    0,
                    0,
                    20.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 10.0,
                "maximum": 20.0,
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map_rainbow.jpeg")


def test_edges_vertex_attribute_item(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "name": "points",
                "item": 1,
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
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_attribute_item.jpeg")


HAT_ATTRIBUTE = {
    "name": "lambert2SG",
    "item": 0,
    "points": [0.0, 0, 0, 1.0, 1.0, 1.0, 0, 0],
    "minimum": 0.0,
    "maximum": 1.0,
}


def register_hat_with_edges(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    dataset_factory(data_id=mesh_id, viewable_file="hat.vtp", viewer_elements_type="polygons")
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "name": "hat.vtp"}],
    )
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": True}],
    )
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["width"]["rpc"],
        [{"id": mesh_id, "width": 4}],
    )


def set_edges_vertex_attribute(server: ServerMonitor, attribute: dict[str, object]) -> None:
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [{"id": mesh_id, **attribute}],
    )


def test_polygons_edges_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    register_hat_with_edges(server, dataset_factory)
    set_edges_vertex_attribute(server, HAT_ATTRIBUTE)
    # Polygons keep their constant color, only the edges are colored
    assert server.compare_image("mesh/edges/polygons_edges_vertex_attribute.jpeg")


def test_polygons_edges_shared_scalar_bar(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    register_hat_with_edges(server, dataset_factory)
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
            "attribute"
        ]["rpc"],
        [{"id": mesh_id, **HAT_ATTRIBUTE}],
    )
    set_edges_vertex_attribute(server, HAT_ATTRIBUTE)
    # Same attribute and color map: one scalar bar only
    assert server.compare_image("mesh/edges/polygons_edges_shared_scalar_bar.jpeg")


def test_polygons_edges_attribute_then_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    register_hat_with_edges(server, dataset_factory)
    set_edges_vertex_attribute(server, HAT_ATTRIBUTE)
    server.call(
        VtkMeshEdgesView.mesh_edges_prefix
        + VtkMeshEdgesView.mesh_edges_schemas_dict["color"]["rpc"],
        [{"id": mesh_id, "color": {"red": 255, "green": 0, "blue": 0, "alpha": 1.0}}],
    )
    # Red edges, no edges scalar bar
    assert server.compare_image("mesh/edges/polygons_edges_attribute_then_color.jpeg")


def test_polygons_edges_hidden_with_object(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    register_hat_with_edges(server, dataset_factory)
    set_edges_vertex_attribute(server, HAT_ATTRIBUTE)
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": False}],
    )
    # Empty scene: no edges, no scalar bar
    assert server.compare_image("mesh/edges/polygons_edges_hidden_with_object.jpeg")


def test_polygons_points_and_edges_shared_scalar_bar(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    register_hat_with_edges(server, dataset_factory)
    server.call(
        VtkMeshPointsView.mesh_points_prefix
        + VtkMeshPointsView.mesh_points_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": True}],
    )
    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [{"id": mesh_id, **HAT_ATTRIBUTE}],
    )
    set_edges_vertex_attribute(server, HAT_ATTRIBUTE)
    # Same attribute and color map on points and edges: one scalar bar only
    assert server.compare_image("mesh/edges/polygons_points_and_edges_shared_scalar_bar.jpeg")


def set_polygons_vertex_attribute(server: ServerMonitor) -> None:
    server.call(
        VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_prefix
        + VtkMeshPolygonsAttributeVertexView.mesh_polygons_attribute_vertex_schemas_dict[
            "attribute"
        ]["rpc"],
        [{"id": mesh_id, **HAT_ATTRIBUTE}],
    )


def test_polygons_edges_shared_scalar_bar_edges_first(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    register_hat_with_edges(server, dataset_factory)
    set_edges_vertex_attribute(server, HAT_ATTRIBUTE)
    set_polygons_vertex_attribute(server)
    # Same picture as when the polygons attribute comes first: one scalar bar only
    assert server.compare_image("mesh/edges/polygons_edges_shared_scalar_bar.jpeg")


def test_polygons_color_after_shared_scalar_bar(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_polygons_edges_shared_scalar_bar(server, dataset_factory)
    server.call(
        VtkMeshPolygonsView.mesh_polygons_prefix
        + VtkMeshPolygonsView.mesh_polygons_schemas_dict["color"]["rpc"],
        [{"id": mesh_id, "color": {"red": 255, "green": 255, "blue": 255, "alpha": 1.0}}],
    )
    # Polygons back to a constant color: the edges keep their attribute and get their own bar
    assert server.compare_image("mesh/edges/polygons_color_after_shared_scalar_bar.jpeg")
