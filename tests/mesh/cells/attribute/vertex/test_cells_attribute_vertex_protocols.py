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
        [{"id": mesh_id, "name": "regular_grid_2d.vti"}],
    )


def test_cells_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute, item, range and color map in a single call
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "attribute"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "name": "points",
                "item": 0,
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

    # Set active attribute, item, range and color map
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "attribute"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "name": "points",
                "item": 0,
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
            "attribute"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "name": "points",
                "item": 0,
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

    # Set active attribute, item, range and color map
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "attribute"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "name": "points",
                "item": 0,
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
            "attribute"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "name": "points",
                "item": 0,
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

    # Rainbow Desaturated Map
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "attribute"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "name": "points",
                "item": 0,
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
            "attribute"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "name": "points",
                "item": 0,
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


def test_cells_vertex_vector_component(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register(server, dataset_factory)

    # Set active attribute with a vector component (points, item 1)
    server.call(
        VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_prefix
        + VtkMeshCellsAttributeVertexView.mesh_cells_attribute_vertex_schemas_dict[
            "attribute"
        ]["rpc"],
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
            }
        ],
    )

    # Render and assert we receive non-empty image bytes (no backend crashes)
    server.call("opengeodeweb_viewer.viewer.render")
    while True:
        response = server.ws.recv()
        if isinstance(response, bytes):
            assert len(response) > 0
            break
