# Standard library imports
from typing import Callable

# Third party imports
import os
import json
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.cells.cells_protocols import VtkMeshCellsView
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView

# Local application imports
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "123456789"


def save_image(server: ServerMonitor, filename: str) -> None:
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["render"]["rpc"]
    )
    while True:
        image = server.ws.recv()
        if isinstance(image, bytes):
            response = server.ws.recv()
            result = json.loads(response)["result"]
            if result["stale"]:
                continue
            comparison_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "data", "comparison"
            )
            output_path = os.path.join(comparison_dir, filename)
            with open(output_path, "wb") as f:
                f.write(image)
            print(f"Image saved to {output_path}")
            break


def test_mesh_scalar_range_fixed_lut(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    # 1. Register mesh (points values ~2 to 498)
    dataset_factory(id=mesh_id, viewable_file="regular_grid_2d.vti")
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id}],
    )
    save_image(server, "fixed_lut_1_register.jpeg")

    # 2. Set active attribute "points", should be blue
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_attribute"]["rpc"],
        [{"id": mesh_id, "name": "points"}],
    )
    save_image(server, "fixed_lut_2_attribute.jpeg")

    # 3. Apply a scalarRange of [0, 1]
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 0.0, "maximum": 1.0}],
    )
    save_image(server, "fixed_lut_3_range_0_1.jpeg")

    # 4. Set LUT on [0, 1] (Blue to Red), should be red
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_color_map"]["rpc"],
        [
            {
                "id": mesh_id,
                "points": [
                    [0.0, 0, 0, 1.0],
                    [1.0, 1.0, 0, 0],
                ],
            }
        ],
    )
    save_image(server, "fixed_lut_4_lut_0_1_saturated.jpeg")

    # 5. Modify scalar range to [0, 500] WITHOUT changing the LUT
    server.call(
        VtkMeshCellsView.mesh_cells_prefix
        + VtkMeshCellsView.mesh_cells_schemas_dict["vertex_scalar_range"]["rpc"],
        [{"id": mesh_id, "minimum": 0.0, "maximum": 500.0}],
    )
    save_image(server, "fixed_lut_5_range_500_lut_fixed.jpeg")
