# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.polyhedra.attribute.vertex.polyhedra_attribute_vertex_protocols import (
    VtkMeshPolyhedraAttributeVertexView,
)

# Local application imports
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "123456789"


def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(
        id=mesh_id,
        viewable_file="polyhedron_attribute.vtu",
        viewer_elements_type="polyhedra",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )



def test_polyhedra_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_prefix
        + VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "toto_on_vertices"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_prefix
        + VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    1.0,
                    0,
                    0,
                    1.0,
                    11.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 1.0,
                "maximum": 11.0,
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/vertex_color_map.jpeg") == True


def test_polyhedra_vertex_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_prefix
        + VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "toto_on_vertices"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_prefix
        + VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    1.0,
                    0,
                    0,
                    1.0,
                    11.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 1.0,
                "maximum": 11.0,
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_prefix
        + VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    10.0,
                    0,
                    0,
                    1.0,
                    11.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 10.0,
                "maximum": 11.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/polyhedra/vertex_color_map_range_update.jpeg")
        == True
    )


def test_polyhedra_vertex_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_prefix
        + VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "toto_on_vertices"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_prefix
        + VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    1.0,
                    0,
                    0,
                    1.0,
                    11.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 1.0,
                "maximum": 11.0,
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_prefix
        + VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_schemas_dict[
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

    assert (
        server.compare_image("mesh/polyhedra/vertex_color_map_red_shift.jpeg") == True
    )


def test_polyhedra_vertex_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_prefix
        + VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_schemas_dict[
            "name"
        ][
            "rpc"
        ],
        [{"id": mesh_id, "name": "toto_on_vertices"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_prefix
        + VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    1.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    1.0 + 0.143 * 10,
                    0,
                    0,
                    92 / 255,
                    1.0 + 0.285 * 10,
                    0,
                    255 / 255,
                    255 / 255,
                    1.0 + 0.429 * 10,
                    0,
                    128 / 255,
                    0,
                    1.0 + 0.571 * 10,
                    255 / 255,
                    255 / 255,
                    0,
                    1.0 + 0.714 * 10,
                    255 / 255,
                    97 / 255,
                    0,
                    1.0 + 0.857 * 10,
                    107 / 255,
                    0,
                    0,
                    11.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 1.0,
                "maximum": 11.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/polyhedra/vertex_color_map_rainbow_initial.jpeg")
        == True
    )

    # Update rainbow range via color map
    server.call(
        VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_prefix
        + VtkMeshPolyhedraAttributeVertexView.mesh_polyhedra_attribute_vertex_schemas_dict[
            "color_map"
        ][
            "rpc"
        ],
        [
            {
                "id": mesh_id,
                "points": [
                    2.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    2.0 + 0.143 * 6,
                    0,
                    0,
                    92 / 255,
                    2.0 + 0.285 * 6,
                    0,
                    255 / 255,
                    255 / 255,
                    2.0 + 0.429 * 6,
                    0,
                    128 / 255,
                    0,
                    2.0 + 0.571 * 6,
                    255 / 255,
                    255 / 255,
                    0,
                    2.0 + 0.714 * 6,
                    255 / 255,
                    97 / 255,
                    0,
                    2.0 + 0.857 * 6,
                    107 / 255,
                    0,
                    0,
                    8.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 2.0,
                "maximum": 8.0,
            }
        ],
    )

    assert server.compare_image("mesh/polyhedra/vertex_color_map_rainbow.jpeg") == True
