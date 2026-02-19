# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.edges.attribute.vertex.edges_attribute_vertex_protocols import (
    VtkMeshEdgesAttributeVertexView,
)

# Local application imports
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "123456789"


def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(
        id=mesh_id,
        viewable_file="attributed_edged_curve.vtp",
        viewer_elements_type="edges",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )


def test_edges_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": mesh_id, "name": "vertex_attribute"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict[
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
                    58.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map.jpeg") == True


def test_edges_vertex_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": mesh_id, "name": "vertex_attribute"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict[
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
                    58.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
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
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map_range_update.jpeg") == True


def test_edges_vertex_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": mesh_id, "name": "vertex_attribute"}],
    )

    # Set Blue to Red Map on [0, 58]
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict[
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
                    58.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 58.0,
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict[
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

    assert server.compare_image("mesh/edges/vertex_color_map_red_shift.jpeg") == True


def test_edges_vertex_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": mesh_id, "name": "vertex_attribute"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict[
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
            }
        ],
    )

    assert (
        server.compare_image("mesh/edges/vertex_color_map_rainbow_initial.jpeg") == True
    )

    # Update rainbow range via color map
    server.call(
        VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_prefix
        + VtkMeshEdgesAttributeVertexView.mesh_edges_attribute_vertex_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
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
            }
        ],
    )

    assert server.compare_image("mesh/edges/vertex_color_map_rainbow.jpeg") == True
