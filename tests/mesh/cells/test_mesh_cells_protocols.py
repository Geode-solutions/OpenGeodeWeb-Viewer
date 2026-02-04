# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.cells.cells_protocols import VtkMeshCellsView

# Local application imports
from tests.mesh.test_mesh_protocols import test_register_mesh
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "123456789"


def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(
        id=mesh_id, viewable_file="regular_grid_2d.vti", viewer_elements_type="polygons"
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )
    assert server.compare_image("mesh/cells/register.jpeg") == True


def test_cells_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["color"]["rpc"],
        [{"id": mesh_id, "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("mesh/cells/color.jpeg") == True


def test_cells_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": False}],
    )
    assert server.compare_image("mesh/cells/visibility.jpeg") == True


def test_cells_vertex_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "points"}],
    )
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 2, "maximum": 498}],
    )
    assert server.compare_image("mesh/cells/vertex_attribute.jpeg") == True

    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 0, "maximum": 10}],
    )
    assert server.compare_image("mesh/cells/vertex_scalar_range.jpeg") == True


def test_cells_cell_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_attribute"]["rpc"],
        [{"id": mesh_id, "name": "RGB_data"}],
    )
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 0, "maximum": 255}],
    )
    assert server.compare_image("mesh/cells/cell_attribute.jpeg") == True

    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 0, "maximum": 10}],
    )
    assert server.compare_image("mesh/cells/cell_scalar_range.jpeg") == True


def test_cells_vertex_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "points"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "points"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "points"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "points"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_color_map"]["rpc"],
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


def test_cells_cell_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    # Set active attribute
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_attribute"]["rpc"],
        [{"id": mesh_id, "name": "RGB_data"}],
    )

    # Set color map: Blue to Red
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_attribute"]["rpc"],
        [{"id": mesh_id, "name": "RGB_data"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_attribute"]["rpc"],
        [{"id": mesh_id, "name": "RGB_data"}],
    )

    # Set Blue to Red Map
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_attribute"]["rpc"],
        [{"id": mesh_id, "name": "RGB_data"}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_color_map"]["rpc"],
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
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_color_map"]["rpc"],
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
