# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.cells.attribute.vertex.cells_attribute_vertex_protocols import (
    VtkMeshCellsAttributeVertexView,
)

# Local application imports
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "123456789"


def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(
        id=mesh_id, viewable_file="regular_grid_2d.vti", viewer_elements_type="cells"
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )


def test_cells_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": mesh_id, "name": "points"}],
    )
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "scalar_range"
        ]["rpc"],
        [{"id": mesh_id, "minimum": 2, "maximum": 498}],
    )
    assert server.compare_image("mesh/cells/vertex_attribute.jpeg") == True

    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "scalar_range"
        ]["rpc"],
        [{"id": mesh_id, "minimum": 0, "maximum": 10}],
    )
    assert server.compare_image("mesh/cells/vertex_scalar_range.jpeg") == True


def test_cells_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": mesh_id, "name": "points"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
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
            }
        ],
    )

    assert server.compare_image("mesh/cells/vertex_color_map.jpeg") == True


def test_cells_vertex_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": mesh_id, "name": "points"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
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
            }
        ],
    )

    assert server.compare_image("mesh/cells/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    200.0,
                    0,
                    0,
                    1.0,
                    300.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 200.0,
                "maximum": 300.0,
            }
        ],
    )

    assert server.compare_image("mesh/cells/vertex_color_map_range_update.jpeg") == True


def test_cells_vertex_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": mesh_id, "name": "points"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
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
            }
        ],
    )

    assert server.compare_image("mesh/cells/vertex_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
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

    assert server.compare_image("mesh/cells/vertex_color_map_red_shift.jpeg") == True


def test_cells_vertex_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "name"
        ]["rpc"],
        [{"id": mesh_id, "name": "points"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
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
                    2.0 + 0.143 * 496,
                    0,
                    0,
                    92 / 255,
                    2.0 + 0.285 * 496,
                    0,
                    255 / 255,
                    255 / 255,
                    2.0 + 0.429 * 496,
                    0,
                    128 / 255,
                    0,
                    2.0 + 0.571 * 496,
                    255 / 255,
                    255 / 255,
                    0,
                    2.0 + 0.714 * 496,
                    255 / 255,
                    97 / 255,
                    0,
                    2.0 + 0.857 * 496,
                    107 / 255,
                    0,
                    0,
                    498.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 2.0,
                "maximum": 498.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/cells/vertex_color_map_rainbow_initial.jpeg") == True
    )

    # Set scalar range via color map
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    50.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    50.0 + 0.143 * 150,
                    0,
                    0,
                    92 / 255,
                    50.0 + 0.285 * 150,
                    0,
                    255 / 255,
                    255 / 255,
                    50.0 + 0.429 * 150,
                    0,
                    128 / 255,
                    0,
                    50.0 + 0.571 * 150,
                    255 / 255,
                    255 / 255,
                    0,
                    50.0 + 0.714 * 150,
                    255 / 255,
                    97 / 255,
                    0,
                    50.0 + 0.857 * 150,
                    107 / 255,
                    0,
                    0,
                    200.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 50.0,
                "maximum": 200.0,
            }
        ],
    )

    assert server.compare_image("mesh/cells/vertex_color_map_rainbow.jpeg") == True
