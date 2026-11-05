from typing import TYPE_CHECKING

import pytest
from vtkmodules.vtkCommonCore import reference, vtkFloatArray
from vtkmodules.vtkFiltersSources import vtkPlaneSource
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader, vtkXMLPolyDataWriter
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkTexture

from opengeodeweb_viewer.basemap_drape import (
    DRAPE_POLYGON_OFFSET_UNITS,
    clipped_to_bounds,
    drape_actor,
    drape_polydata,
    top_surfaces,
    upward_ratio,
)
from opengeodeweb_viewer.basemap_pipeline import pipeline_surfaces
from opengeodeweb_viewer.vtk_pipeline import VtkPipeline

if TYPE_CHECKING:
    from pathlib import Path

    from vtkmodules.vtkCommonDataModel import vtkPolyData


def _plane(
    origin: tuple[float, float, float],
    point1: tuple[float, float, float],
    point2: tuple[float, float, float],
    resolution: int = 1,
) -> vtkPolyData:
    plane = vtkPlaneSource()
    plane.SetOrigin(origin)
    plane.SetPoint1(point1)
    plane.SetPoint2(point2)
    plane.SetResolution(resolution, resolution)
    plane.Update()
    return plane.GetOutput()


def _horizontal(z: float) -> vtkPolyData:
    return _plane((0, 0, z), (10, 0, z), (0, 10, z))


def _wall(z_top: float) -> vtkPolyData:
    return _plane((0, 0, z_top - 10), (10, 0, z_top - 10), (0, 0, z_top))


def _basemap(z: float = 0.0) -> vtkPolyData:
    basemap = _plane((-10, -10, z), (30, -10, z), (-10, 30, z), resolution=4)
    uv = vtkFloatArray()
    uv.SetName("basemap_uv")
    uv.SetNumberOfComponents(2)
    for index in range(basemap.GetNumberOfPoints()):
        x, y, _ = basemap.GetPoint(index)
        uv.InsertNextTuple2((x + 10) / 40, (y + 10) / 40)
    basemap.GetPointData().AddArray(uv)
    return basemap


def test_upward_ratio() -> None:
    assert upward_ratio(_horizontal(0)) == pytest.approx(1)
    assert upward_ratio(_wall(0)) == pytest.approx(0, abs=1e-9)
    # Normals pointing down: still a horizontal surface
    flipped = _plane((0, 0, 0), (0, 10, 0), (10, 0, 0))
    assert upward_ratio(flipped) == pytest.approx(1)


def test_top_surfaces_keeps_the_topography_only() -> None:
    topography = _horizontal(0)
    horizon = _horizontal(-500)
    wall = _wall(0)
    # Within 1 % of a 600 m extent
    almost_top = _horizontal(-5)
    kept = top_surfaces(
        [topography, horizon, wall, almost_top], data_top=0, z_extent=600
    )
    assert kept == [topography, almost_top]


def test_top_surfaces_tolerance_is_at_least_one_metre() -> None:
    assert top_surfaces([_horizontal(-0.5)], data_top=0, z_extent=10) != []
    assert top_surfaces([_horizontal(-2)], data_top=0, z_extent=10) == []


def test_drape_polydata_reads_the_basemap_uv_above_each_point() -> None:
    surface = _horizontal(-50)
    drape = drape_polydata([surface, _horizontal(-60)], _basemap(z=0))
    assert drape.GetNumberOfCells() == 2 * surface.GetNumberOfCells()
    tcoords = drape.GetPointData().GetTCoords()
    assert tcoords is not None
    # Each point gets the basemap uv right above it, whatever its height
    for index in range(drape.GetNumberOfPoints()):
        x, y, _ = drape.GetPoint(index)
        assert tcoords.GetTuple2(index) == pytest.approx(((x + 10) / 40, (y + 10) / 40))


def test_drape_actor_shows_the_full_texture() -> None:
    texture = vtkTexture()
    actor = drape_actor(_horizontal(0), texture)
    assert actor.GetTexture() is texture
    assert not actor.GetPickable()
    assert not actor.GetProperty().GetLighting()
    factor, units = reference(0.0), reference(0.0)
    actor.GetMapper().GetRelativeCoincidentTopologyPolygonOffsetParameters(
        factor, units
    )
    assert (factor.get(), units.get()) == (0.0, DRAPE_POLYGON_OFFSET_UNITS)


def test_pipeline_surfaces_of_a_surface_mesh(tmp_path: Path) -> None:
    path = tmp_path / "surface.vtp"
    writer = vtkXMLPolyDataWriter()
    writer.SetFileName(str(path))
    writer.SetInputData(_horizontal(0))
    writer.Write()
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(str(path))
    reader.Update()
    pipeline = VtkPipeline(reader, vtkDataSetMapper())
    pipeline.filter.SetInputConnection(reader.GetOutputPort())
    pipeline.filter.Update()
    [surface] = pipeline_surfaces(pipeline)
    assert surface.GetNumberOfPolys() == 1
    # Hidden data is never draped
    pipeline.actor.VisibilityOff()
    assert pipeline_surfaces(pipeline) == []


def test_surfaces_clipped_to_the_detail_bounds() -> None:
    # A 10 x 10 surface; the detail covers its left half only
    surface = _horizontal(0)
    [clipped] = clipped_to_bounds([surface], (0.0, 5.0, 0.0, 10.0, -1.0, 1.0))
    x_min, x_max, _, _, _, _ = clipped.GetBounds()
    assert x_min >= 0.0
    assert x_max <= 5.0 + 1e-9
    assert clipped_to_bounds([surface], (100.0, 110.0, 0.0, 10.0, -1.0, 1.0)) == []
