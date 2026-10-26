import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from vtkmodules.vtkCommonCore import reference
from vtkmodules.vtkRenderingCore import vtkActor, vtkDataSetMapper

from opengeodeweb_viewer.rpc.mesh.mesh_protocols import (
    VtkMeshView,
    check_tiles_folder,
    style_basemap,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.conftest import ServerMonitor

# Local constants
mesh_id = "12345678901234567890123456789012"


def test_register_mesh(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    dataset_factory(data_id=mesh_id, viewable_file="hat.vtp", viewer_elements_type="polygons")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "name": "hat.vtp"}],
    )
    assert server.compare_image("mesh/register.jpeg")


def test_deregister_mesh(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["deregister"]["rpc"],
        [{"id": mesh_id}],
    )

    assert server.compare_image("mesh/deregister.jpeg")


def test_visibility(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": False}],
    )
    assert server.compare_image("mesh/visibility.jpeg")


def test_color(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["color"]["rpc"],
        [
            {
                "id": mesh_id,
                "color": {"red": 50, "green": 2, "blue": 250, "alpha": 1.0},
            }
        ],
    )
    assert server.compare_image("mesh/color.jpeg")


def test_apply_textures(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)
    dataset_factory(
        data_id="00000000000000000000000987654321",
        viewable_file="hat_lambert2SG.vti",
        viewer_elements_type="polygons",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["apply_textures"]["rpc"],
        [
            {
                "id": mesh_id,
                "textures": [
                    {
                        "texture_name": "lambert2SG",
                        "id": "00000000000000000000000987654321",
                    }
                ],
            }
        ],
    )
    assert server.compare_image("mesh/apply_textures.jpeg")


def _apply_basemap(server: ServerMonitor, dataset_factory: Callable[..., str]) -> str:
    basemap_id = "0000000000000000000000000basemap"
    dataset_factory(
        data_id=basemap_id, viewable_file="basemap.vtp", viewer_elements_type="polygons"
    )
    shutil.copytree(
        Path(__file__).parent.parent / "data" / "basemap_tiles",
        Path(os.environ["DATA_FOLDER_PATH"]) / basemap_id / "basemap_tiles",
        dirs_exist_ok=True,
    )
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": basemap_id, "name": "basemap"}],
    )
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["apply_basemap"]["rpc"],
        [{"id": basemap_id, "tiles_folder": "basemap_tiles", "columns": 2, "rows": 2}],
    )
    return basemap_id


def test_apply_basemap(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    _apply_basemap(server, dataset_factory)
    assert server.compare_image("mesh/apply_basemap.jpeg")


def test_basemap_opacity(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    basemap_id = _apply_basemap(server, dataset_factory)
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["basemap_opacity"]["rpc"],
        [{"id": basemap_id, "opacity": 0.5}],
    )
    assert server.compare_image("mesh/basemap_opacity.jpeg")


def test_basemap_style_stays_behind_the_data() -> None:
    actor = vtkActor()
    mapper = vtkDataSetMapper()
    style_basemap(actor, mapper)
    # Positive offsets push the basemap away from flat data at the same height
    factor, units = reference(0.0), reference(0.0)
    mapper.GetRelativeCoincidentTopologyPolygonOffsetParameters(factor, units)
    assert (factor.get(), units.get()) == (4.0, 4.0)
    assert not actor.GetPickable()
    assert not actor.GetProperty().GetLighting()


@pytest.mark.parametrize("name", ["", ".", "..", "../other", "a/b", "a\\b", "/etc"])
def test_tiles_folder_must_be_a_plain_name(name: str) -> None:
    with pytest.raises(ValueError, match="tiles_folder"):
        check_tiles_folder(name)


def test_tiles_folder_plain_name() -> None:
    check_tiles_folder("tiles")
