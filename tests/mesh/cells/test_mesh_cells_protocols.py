# Standard library imports
from typing import Callable

# Third party imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.cells.cells_protocols import VtkMeshCellsView
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView

# Local application imports
from tests.mesh.test_mesh_protocols import test_register_mesh
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "12345678901234567890123456789012"


def test_register(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    dataset_factory(
        id=mesh_id, viewable_file="regular_grid_2d.vti", viewer_elements_type="cells"
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "name": "regular_grid_2d.vti"}],
    )
    assert server.compare_image("mesh/cells/register.jpeg") == True


def test_cells_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["color"]["rpc"],
        [{"id": mesh_id, "color": {"red": 255, "green": 0, "blue": 0, "alpha": 0.5}}],
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


def test_cells_clipping_plane(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["clipping_planes"]["rpc"],
        [
            {
                "ids": [mesh_id],
                "planes": [
                    {
                        "origin": [262.0, 387.0, 0.0],
                        "normal": [1.0, 1.0, 0.0],
                    }
                ],
            }
        ],
    )
    assert server.compare_image("mesh/cells/clipping_plane.jpeg") == True


def test_cells_shrink(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register(server, dataset_factory)

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["shrink"]["rpc"],
        [
            {
                "ids": [mesh_id],
                "shrink_factor": 0.8,
            }
        ],
    )
    assert server.compare_image("mesh/cells/shrink.jpeg") == True


grid_3d_id = "22345678901234567890123456789012"
other_mesh_id = "32345678901234567890123456789012"
slice_rpc = (
    VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["slice"]["rpc"]
)


def register_grid_3d(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    dataset_factory(
        id=grid_3d_id,
        viewable_file="regular_grid_3d.vti",
        viewer_elements_type="cells",
    )
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": grid_3d_id, "name": "regular_grid_3d.vti"}],
    )
    assert server.compare_image("mesh/cells/slice_grid_3d_register.jpeg") == True


def call_slice(
    server: ServerMonitor, ids: list[str], slices: list[dict[str, int]]
) -> object:
    server.call(slice_rpc, [{"ids": ids, "slices": slices}])
    response = server.get_response()
    assert isinstance(response, dict), f"Unexpected response: {response!r}"
    return response["result"]


def test_slice(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    register_grid_3d(server, dataset_factory)

    result = call_slice(server, [grid_3d_id], [{"axis": 2, "index": 3}])
    assert result == {"max_indices": [10, 8, 6]}
    assert server.compare_image("mesh/cells/slice_grid_3d.jpeg") == True


def test_slice_clamped(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register(server, dataset_factory)

    result = call_slice(server, [mesh_id], [{"axis": 0, "index": 10000}])
    assert result == {"max_indices": [524, 774, 0]}
    assert server.compare_image("mesh/cells/slice_grid_2d_last.jpeg") == True

    call_slice(server, [mesh_id], [{"axis": 0, "index": 524}])
    assert server.compare_image("mesh/cells/slice_grid_2d_last.jpeg") == True


def test_slice_removed(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    register_grid_3d(server, dataset_factory)
    call_slice(server, [grid_3d_id], [{"axis": 2, "index": 3}])

    result = call_slice(server, [grid_3d_id], [])
    assert result == {"max_indices": [10, 8, 6]}
    assert server.compare_image("mesh/cells/slice_grid_3d_register.jpeg") == True


def test_slice_then_clipping(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    register_grid_3d(server, dataset_factory)
    call_slice(server, [grid_3d_id], [{"axis": 2, "index": 3}])

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["clipping_planes"]["rpc"],
        [
            {
                "ids": [grid_3d_id],
                "planes": [{"origin": [50.0, 40.0, 30.0], "normal": [1.0, 0.0, 0.0]}],
            }
        ],
    )
    assert server.compare_image("mesh/cells/slice_grid_3d_clipping.jpeg") == True


def test_slice_grid_2d(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register(server, dataset_factory)

    result = call_slice(server, [mesh_id], [{"axis": 0, "index": 262}])
    assert result == {"max_indices": [524, 774, 0]}
    assert server.compare_image("mesh/cells/slice_grid_2d.jpeg") == True


def test_slice_on_non_grid_removed(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    dataset_factory(
        id=other_mesh_id, viewable_file="hat.vtp", viewer_elements_type="polygons"
    )
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": other_mesh_id, "name": "hat.vtp"}],
    )
    server.get_response()

    result = call_slice(server, [other_mesh_id], [])
    assert result == {"max_indices": [0, 0, 0]}


def test_slice_on_non_grid_ignored(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    register_grid_3d(server, dataset_factory)
    dataset_factory(
        id=other_mesh_id, viewable_file="hat.vtp", viewer_elements_type="polygons"
    )
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": other_mesh_id, "name": "hat.vtp"}],
    )
    server.get_response()

    result = call_slice(server, [other_mesh_id, grid_3d_id], [{"axis": 2, "index": 3}])
    assert result == {"max_indices": [10, 8, 6]}


def test_multiple_slices(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register(server, dataset_factory)

    result = call_slice(
        server,
        [mesh_id],
        [
            {"axis": 0, "index": 100},
            {"axis": 0, "index": 400},
            {"axis": 1, "index": 387},
        ],
    )
    assert result == {"max_indices": [524, 774, 0]}
    assert server.compare_image("mesh/cells/slice_grid_2d_multiple.jpeg") == True
