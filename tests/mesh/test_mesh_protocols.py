import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkFiltersSources import vtkCubeSource, vtkPlaneSource
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor
from vtkmodules.vtkRenderingCore import vtkActor, vtkDataSetMapper, vtkPolyDataMapper, vtkRenderer

from opengeodeweb_viewer.rpc.mesh.mesh_protocols import (
    TILES_FOLDER,
    VtkMeshView,
    check_source_folder,
)
from opengeodeweb_viewer.rpc.viewer.schemas.clipping_planes import Plane
from opengeodeweb_viewer.vtk_pipeline import BasemapState, VtkPipeline
from opengeodeweb_viewer.vtk_protocol import VtkView, basemap_clipping_filter

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
        Path(os.environ["DATA_FOLDER_PATH"]) / basemap_id / TILES_FOLDER,
        dirs_exist_ok=True,
    )
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": basemap_id, "name": "basemap"}],
    )
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["apply_basemap"]["rpc"],
        [
            {
                "id": basemap_id,
                "columns": 2,
                "rows": 2,
                "maps": [{"map": "satellite", "sources": ["base"]}],
                "layers": [{"map": "satellite", "visible": True, "opacity": 1.0, "crop": False}],
            }
        ],
    )
    return basemap_id


def test_apply_basemap(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    _apply_basemap(server, dataset_factory)
    assert server.compare_image("mesh/apply_basemap.jpeg")


def test_basemap_layers(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    basemap_id = _apply_basemap(server, dataset_factory)
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["basemap_layers"]["rpc"],
        [
            {
                "id": basemap_id,
                "layers": [{"map": "satellite", "visible": True, "opacity": 0.5, "crop": False}],
            }
        ],
    )
    assert server.compare_image("mesh/basemap_layers.jpeg")


def test_basemap_drape(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    basemap_id = _apply_basemap(server, dataset_factory)
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["basemap_drape"]["rpc"],
        [{"id": basemap_id, "data_ids": []}],
    )
    # Nothing to drape: the flat map stays
    assert server.compare_image("mesh/apply_basemap.jpeg")


@pytest.mark.parametrize("name", ["", ".", "..", "../other", "a/b", "a\\b", "/etc"])
def test_source_folder_must_be_a_plain_name(name: str) -> None:
    with pytest.raises(ValueError, match="basemap source"):
        check_source_folder(name)


def _actor(bounds: tuple[float, float, float, float, float, float]) -> vtkActor:
    cube = vtkCubeSource()
    cube.SetBounds(bounds)
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(cube.GetOutputPort())
    actor = vtkActor()
    actor.SetMapper(mapper)
    return actor


def test_grid_scale_ignores_the_basemap() -> None:
    renderer = vtkRenderer()
    data = _actor((0, 10, 0, 10, -5, 0))
    basemap = _actor((-100, 100, -100, 100, 0, 0))
    renderer.AddActor(data)
    renderer.AddActor(basemap)
    grid_scale = vtkCubeAxesActor()
    VtkView.fit_grid_scale_to_visible_props(grid_scale, renderer, {basemap})
    assert list(grid_scale.GetBounds()) == pytest.approx([0, 10, 0, 10, -5, 0])


def test_basemap_clipping_keeps_texture_coordinates() -> None:
    plane = vtkPlaneSource()
    plane.SetOrigin(0, 0, 0)
    plane.SetPoint1(10, 0, 0)
    plane.SetPoint2(0, 10, 0)
    plane.Update()
    basemap = plane.GetOutput()
    # Keep x <= 4: the cut is exact, not along the coarse basemap cells
    clip = basemap_clipping_filter([Plane(normal=[1, 0, 0], origin=[4, 0, 0])])
    clip.SetInputData(basemap)
    geometry = vtkGeometryFilter()
    geometry.SetInputConnection(clip.GetOutputPort())
    geometry.Update()
    output = geometry.GetOutput()
    assert output.GetBounds()[1] == pytest.approx(4)
    assert output.GetPointData().GetTCoords() is not None


class _SharedObjects:
    def __init__(self) -> None:
        self.objects: dict[str, object] = {"db": {}}

    def getSharedObject(self, key: str) -> object:  # noqa: N802 wslink API
        return self.objects.get(key)

    def setSharedObject(self, key: str, value: object) -> None:  # noqa: N802 wslink API
        self.objects[key] = value


def _view_with_basemap() -> tuple[VtkView, VtkPipeline]:
    """A view holding a basemap draped on "data", and an "other" data."""
    view = VtkView()
    view.coreServer = _SharedObjects()
    database = view.get_data_base()
    for data_id in ("data", "other", "basemap"):
        reader = vtkXMLPolyDataReader()
        reader.SetFileName(str(Path(__file__).parent.parent / "data" / "basemap.vtp"))
        reader.Update()
        database[data_id] = VtkPipeline(reader, vtkDataSetMapper())
    basemap = database["basemap"]
    basemap.basemap = BasemapState(maps=[], images={}, layers={}, drape_ids=["data"])
    return view, basemap


def test_basemap_follows_the_clipping_of_its_draped_data() -> None:
    view, basemap = _view_with_basemap()
    view.set_clipping_planes(["data"], [Plane(normal=[1, 0, 0], origin=[4, 0, 0])])
    assert basemap.clipping_filter is not None
    # Unclipping data the basemap does not lie over leaves it cut
    view.set_clipping_planes(["other"], [])
    assert basemap.clipping_filter is not None
    view.set_clipping_planes(["data"], [])
    assert basemap.clipping_filter is None


def test_basemap_drape_dirty_only_for_its_draped_data() -> None:
    view, _ = _view_with_basemap()
    view.set_shrink(["other"], 0.5)
    assert not view.getSharedObject("basemaps_dirty")
    view.set_shrink(["data"], 0.5)
    assert view.getSharedObject("basemaps_dirty")
