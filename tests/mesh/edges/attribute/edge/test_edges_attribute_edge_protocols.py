# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.edges.attribute.edge.edges_attribute_edge_protocols import (
    VtkMeshEdgesAttributeEdgeView,
)

# Local application imports
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "123456789"


def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(
        id=mesh_id,
        viewable_file="edged_curve3D.vtp",
        viewer_elements_type="edges",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )


def test_edges_edge_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute (cycle_id)
    server.call(
        VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_prefix
        + VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_schemas_dict["name"]["rpc"],
        [{"id": mesh_id, "name": "cycle_id"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_prefix
        + VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    8.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 8.0,
            }
        ],
    )

    assert server.compare_image("mesh/edges/edge_color_map.jpeg") == True


def test_edges_edge_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_prefix
        + VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_schemas_dict["name"]["rpc"],
        [{"id": mesh_id, "name": "cycle_id"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_prefix
        + VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    0,
                    0,
                    1.0,
                    8.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 8.0,
            }
        ],
    )

    assert server.compare_image("mesh/edges/edge_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_prefix
        + VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    4.0,
                    0,
                    0,
                    1.0,
                    8.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 4.0,
                "maximum": 8.0,
            }
        ],
    )

    assert server.compare_image("mesh/edges/edge_color_map_range_update.jpeg") == True


def test_edges_edge_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_prefix
        + VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_schemas_dict["name"]["rpc"],
        [{"id": mesh_id, "name": "cycle_id"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_prefix
        + VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    0.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    0.143 * 8,
                    0,
                    0,
                    92 / 255,
                    0.285 * 8,
                    0,
                    255 / 255,
                    255 / 255,
                    0.429 * 8,
                    0,
                    128 / 255,
                    0,
                    0.571 * 8,
                    255 / 255,
                    255 / 255,
                    0,
                    0.714 * 8,
                    255 / 255,
                    97 / 255,
                    0,
                    0.857 * 8,
                    107 / 255,
                    0,
                    0,
                    8.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 0.0,
                "maximum": 8.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/edges/edge_color_map_rainbow_initial.jpeg") == True
    )

    # Update rainbow range via color map
    server.call(
        VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_prefix
        + VtkMeshEdgesAttributeEdgeView.mesh_edges_attribute_edge_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    2.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    2.0 + 0.143 * 4,
                    0,
                    0,
                    92 / 255,
                    2.0 + 0.285 * 4,
                    0,
                    255 / 255,
                    255 / 255,
                    2.0 + 0.429 * 4,
                    0,
                    128 / 255,
                    0,
                    2.0 + 0.571 * 4,
                    255 / 255,
                    255 / 255,
                    0,
                    2.0 + 0.714 * 4,
                    255 / 255,
                    97 / 255,
                    0,
                    2.0 + 0.857 * 4,
                    107 / 255,
                    0,
                    0,
                    6.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 2.0,
                "maximum": 6.0,
            }
        ],
    )

    assert server.compare_image("mesh/edges/edge_color_map_rainbow.jpeg") == True
