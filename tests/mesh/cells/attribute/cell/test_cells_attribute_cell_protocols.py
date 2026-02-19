# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.cells.attribute.cell.cells_attribute_cell_protocols import (
    VtkMeshCellsAttributeCellView,
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



def test_cells_cell_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_prefix
        + VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_schemas_dict["name"][
            "rpc"
        ],
        [{"id": mesh_id, "name": "RGB_data"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_prefix
        + VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_schemas_dict[
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
                    255.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 255.0,
            }
        ],
    )

    assert server.compare_image("mesh/cells/cell_color_map.jpeg") == True


def test_cells_cell_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_prefix
        + VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_schemas_dict["name"][
            "rpc"
        ],
        [{"id": mesh_id, "name": "RGB_data"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_prefix
        + VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_schemas_dict[
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
                    255.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 255.0,
            }
        ],
    )

    assert server.compare_image("mesh/cells/cell_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_prefix
        + VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_schemas_dict[
            "color_map"
        ]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    100.0,
                    0,
                    0,
                    1.0,
                    150.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 100.0,
                "maximum": 150.0,
            }
        ],
    )

    assert server.compare_image("mesh/cells/cell_color_map_range_update.jpeg") == True


def test_cells_cell_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_prefix
        + VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_schemas_dict["name"][
            "rpc"
        ],
        [{"id": mesh_id, "name": "RGB_data"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_prefix
        + VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_schemas_dict[
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
                    255.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 255.0,
            }
        ],
    )

    assert server.compare_image("mesh/cells/cell_color_map.jpeg") == True

    # Update range via color map
    server.call(
        VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_prefix
        + VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_schemas_dict[
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
                    20.0,
                    1.0,
                    0,
                    0,
                ],
                "minimum": 0.0,
                "maximum": 20.0,
            }
        ],
    )

    assert server.compare_image("mesh/cells/cell_color_map_red_shift.jpeg") == True


def test_cells_cell_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_prefix
        + VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_schemas_dict["name"][
            "rpc"
        ],
        [{"id": mesh_id, "name": "RGB_data"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_prefix
        + VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_schemas_dict[
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
                    0.143 * 255,
                    0,
                    0,
                    92 / 255,
                    0.285 * 255,
                    0,
                    255 / 255,
                    255 / 255,
                    0.429 * 255,
                    0,
                    128 / 255,
                    0,
                    0.571 * 255,
                    255 / 255,
                    255 / 255,
                    0,
                    0.714 * 255,
                    255 / 255,
                    97 / 255,
                    0,
                    0.857 * 255,
                    107 / 255,
                    0,
                    0,
                    255.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 0.0,
                "maximum": 255.0,
            }
        ],
    )

    assert (
        server.compare_image("mesh/cells/cell_color_map_rainbow_initial.jpeg") == True
    )

    # Update range via color map
    server.call(
        VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_prefix
        + VtkMeshCellsAttributeCellView.mesh_cells_attribute_cell_schemas_dict[
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
                    50.0 + 0.143 * 50,
                    0,
                    0,
                    92 / 255,
                    50.0 + 0.285 * 50,
                    0,
                    255 / 255,
                    255 / 255,
                    50.0 + 0.429 * 50,
                    0,
                    128 / 255,
                    0,
                    50.0 + 0.571 * 50,
                    255 / 255,
                    255 / 255,
                    0,
                    50.0 + 0.714 * 50,
                    255 / 255,
                    97 / 255,
                    0,
                    50.0 + 0.857 * 50,
                    107 / 255,
                    0,
                    0,
                    100.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 50.0,
                "maximum": 100.0,
            }
        ],
    )

    assert server.compare_image("mesh/cells/cell_color_map_rainbow.jpeg") == True
