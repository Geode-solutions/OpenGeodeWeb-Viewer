"""Basemap draped on the top surfaces of the georeferenced data."""

# Standard library imports
from __future__ import annotations

from typing import TYPE_CHECKING, cast

# Third party imports
import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkAppendPolyData, vtkProbeFilter, vtkTriangleFilter
from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper

if TYPE_CHECKING:
    from vtkmodules.vtkCommonCore import vtkDataArray

MIN_UPWARD_RATIO = 0.7
TOP_TOLERANCE_RATIO = 0.01
MIN_TOP_TOLERANCE = 1.0
# Pulls the drape in front of the data surface it lies on (units 0), but not in front of
# its points and highlight (-2) nor its edges (-4)
DRAPE_POLYGON_OFFSET_UNITS = -1.0


def _to_numpy(array: vtkDataArray) -> np.ndarray:
    return cast("np.ndarray", vtk_to_numpy(array))  # type: ignore[no-untyped-call]


def _to_vtk(array: np.ndarray) -> vtkDataArray:
    return cast("vtkDataArray", numpy_to_vtk(array, deep=True))  # type: ignore[no-untyped-call]


def upward_ratio(surface: vtkPolyData) -> float:
    """Area weighted mean of |normal z|: 1 when horizontal, 0 when vertical.

    The absolute value keeps surfaces whose normals point down.
    """
    triangles = vtkTriangleFilter()
    triangles.SetInputData(surface)
    triangles.PassLinesOff()
    triangles.PassVertsOff()
    triangles.Update()
    output = triangles.GetOutput()
    if output.GetNumberOfPolys() == 0:
        return 0.0
    points = _to_numpy(output.GetPoints().GetData()).astype(float)
    cells = _to_numpy(output.GetPolys().GetConnectivityArray()).reshape(-1, 3)
    first, second, third = points[cells[:, 0]], points[cells[:, 1]], points[cells[:, 2]]
    cross = np.cross(second - first, third - first)
    areas = float(np.linalg.norm(cross, axis=1).sum())
    if areas == 0:
        return 0.0
    return float(np.abs(cross[:, 2]).sum() / areas)


def top_surfaces(
    surfaces: list[vtkPolyData], data_top: float, z_extent: float
) -> list[vtkPolyData]:
    """Surfaces touching the top of the data and facing up, like a topography."""
    tolerance = max(MIN_TOP_TOLERANCE, TOP_TOLERANCE_RATIO * z_extent)
    # Bounds are cached by VTK: deep surfaces are discarded before any normal is computed
    touching = [
        surface
        for surface in surfaces
        if surface.GetNumberOfPolys() > 0 and surface.GetBounds()[5] >= data_top - tolerance
    ]
    return [surface for surface in touching if upward_ratio(surface) >= MIN_UPWARD_RATIO]


def drape_polydata(surfaces: list[vtkPolyData], basemap: vtkPolyData) -> vtkPolyData:
    """The surfaces in one polydata, textured with the basemap_uv right above each point."""
    append = vtkAppendPolyData()
    for surface in surfaces:
        # Geometry only: the data attributes stay on the data
        geometry = vtkPolyData()
        geometry.SetPoints(surface.GetPoints())
        geometry.SetPolys(surface.GetPolys())
        append.AddInputData(geometry)
    append.Update()
    drape = cast("vtkPolyData", append.GetOutput())
    # The basemap is flat: probe at its height
    coordinates = _to_numpy(drape.GetPoints().GetData()).astype(float)
    coordinates[:, 2] = basemap.GetBounds()[5]
    flat_points = vtkPoints()
    flat_points.SetData(_to_vtk(coordinates))
    flat = vtkPolyData()
    flat.SetPoints(flat_points)
    probe = vtkProbeFilter()
    probe.SetInputData(flat)
    probe.SetSourceData(basemap)
    probe.Update()
    drape.GetPointData().SetTCoords(probe.GetOutput().GetPointData().GetArray("basemap_uv"))
    return drape


def flat_map_lift(basemap_top: float, draped_bottom: float | None, explode_lift: float) -> float:
    """Z offset of the flat map: under the draped relief, or on top of the exploded data."""
    if draped_bottom is not None:
        return draped_bottom - basemap_top
    return explode_lift


def flat_map_visible(*, around: bool, draped: bool) -> bool:
    # Hiding the flat map with nothing draped would hide the whole map
    return around or not draped


def drape_actor(drape: vtkPolyData, basemap_actor: vtkActor) -> vtkActor:
    mapper = vtkPolyDataMapper()
    mapper.SetInputData(drape)
    mapper.ScalarVisibilityOff()
    mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(0.0, DRAPE_POLYGON_OFFSET_UNITS)
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.SetTexture(basemap_actor.GetTexture())
    properties = actor.GetProperty()
    properties.LightingOff()
    properties.SetAmbient(1.0)
    properties.SetDiffuse(0.0)
    properties.SetOpacity(basemap_actor.GetProperty().GetOpacity())
    actor.PickableOff()
    return actor
