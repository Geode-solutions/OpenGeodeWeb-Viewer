# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.cells.cells_protocols import VtkMeshCellsView

# Local application imports
from tests.mesh.test_mesh_protocols import test_register_mesh
from tests.conftest import ServerMonitor

# Local constants
id = "regular_grid_2d"

def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(id=id, viewable_file=f"{id}.vti")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": id}],
    )
    assert server.compare_image("mesh/cells/register.jpeg") == True

def test_cells_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["color"]["rpc"],
        [{"id": id, "color": {"r": 255, "g": 0, "b": 0}}],
    )
    assert server.compare_image("mesh/cells/color.jpeg") == True


def test_cells_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["visibility"]["rpc"],
        [{"id": id, "visibility": False}],
    )
    assert server.compare_image("mesh/cells/visibility.jpeg") == True
