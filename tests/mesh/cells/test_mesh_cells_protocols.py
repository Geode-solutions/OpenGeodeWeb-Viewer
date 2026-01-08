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

    dataset_factory(id=mesh_id, viewable_file="regular_grid_2d.vti")

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
    assert server.compare_image("mesh/cells/cell_attribute.jpeg") == True

    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["cell_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 0, "maximum": 10}],
    )
    assert server.compare_image("mesh/cells/cell_scalar_range.jpeg") == True
