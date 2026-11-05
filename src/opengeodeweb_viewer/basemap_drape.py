"""Basemap draped on the top surfaces of the georeferenced data."""

from __future__ import annotations

# Standard library imports
from typing import TYPE_CHECKING, cast

# Third party imports
import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPlane, vtkPolyData
from vtkmodules.vtkFiltersCore import (
    vtkAppendPolyData,
    vtkClipPolyData,
    vtkProbeFilter,
    vtkTriangleFilter,
)
from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper, vtkTexture

if TYPE_CHECKING:
    from vtkmodules.vtkCommonCore import vtkDataArray
    from vtkmodules.vtkRenderingCore import vtkMapper

MIN_UPWARD_RATIO = 0.7
TOP_TOLERANCE_RATIO = 0.01
MIN_TOP_TOLERANCE = 1.0
# Added to the global offset (2, 0) of every mapper: the basemap is drawn behind flat data.
# Only a constant depth offset: a slope factor would grow at grazing angles and let the
# data sides just under the basemap show through it
BASEMAP_POLYGON_OFFSET_UNITS = 4.0
# A detail map lies on its base map: one unit closer, still behind flat data
DETAIL_POLYGON_OFFSET_UNITS = BASEMAP_POLYGON_OFFSET_UNITS - 1.0
# Pulls the drape in front of the data surface it lies on (units 0), but not in front of
# its points and highlight (-2) nor its edges (-4)
DRAPE_POLYGON_OFFSET_UNITS = -1.0
# The detail drape lies on the base drape: pulled a bit further, still behind the points
DETAIL_DRAPE_POLYGON_OFFSET_UNITS = DRAPE_POLYGON_OFFSET_UNITS - 0.5


def _to_numpy(array: vtkDataArray) -> np.ndarray:
    return cast("np.ndarray", vtk_to_numpy(array))  # type: ignore[no-untyped-call]


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
        if surface.GetNumberOfPolys() > 0
        and surface.GetBounds()[5] >= data_top - tolerance
    ]
    return [
        surface for surface in touching if upward_ratio(surface) >= MIN_UPWARD_RATIO
    ]


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
    flat_points.SetData(numpy_to_vtk(coordinates, deep=True))  # type: ignore[no-untyped-call]
    flat = vtkPolyData()
    flat.SetPoints(flat_points)
    probe = vtkProbeFilter()
    probe.SetInputData(flat)
    probe.SetSourceData(basemap)
    probe.Update()
    drape.GetPointData().SetTCoords(
        probe.GetOutput().GetPointData().GetArray("basemap_uv")
    )
    return drape


def _clip_half_space(
    surface: vtkPolyData, origin: tuple[float, ...], normal: tuple[float, ...]
) -> vtkPolyData:
    plane = vtkPlane()
    plane.SetOrigin(origin)
    plane.SetNormal(normal)
    clip = vtkClipPolyData()
    clip.SetInputData(surface)
    clip.SetClipFunction(plane)
    clip.Update()
    return cast("vtkPolyData", clip.GetOutput())


def clipped_to_bounds(
    surfaces: list[vtkPolyData], bounds: tuple[float, ...]
) -> list[vtkPolyData]:
    """The parts of the surfaces inside the XY bounds of a detail map."""
    # One plane per side: exact on coarse cells, which a box function interpolates badly
    sides = [
        ((bounds[0], 0.0, 0.0), (1.0, 0.0, 0.0)),
        ((bounds[1], 0.0, 0.0), (-1.0, 0.0, 0.0)),
        ((0.0, bounds[2], 0.0), (0.0, 1.0, 0.0)),
        ((0.0, bounds[3], 0.0), (0.0, -1.0, 0.0)),
    ]
    clipped: list[vtkPolyData] = []
    for surface in surfaces:
        output = surface
        for origin, normal in sides:
            output = _clip_half_space(output, origin, normal)
        if output.GetNumberOfCells() > 0:
            clipped.append(output)
    return clipped


def style_basemap(actor: vtkActor, mapper: vtkMapper, offset_units: float) -> None:
    # Map colours must not be shaded, and the basemap must not catch picks
    properties = actor.GetProperty()
    properties.LightingOff()
    properties.SetAmbient(1.0)
    properties.SetDiffuse(0.0)
    actor.PickableOff()
    mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(0.0, offset_units)


def drape_actor(
    drape: vtkPolyData,
    texture: vtkTexture,
    offset_units: float = DRAPE_POLYGON_OFFSET_UNITS,
) -> vtkActor:
    mapper = vtkPolyDataMapper()
    mapper.SetInputData(drape)
    mapper.ScalarVisibilityOff()
    actor = vtkActor()
    actor.SetMapper(mapper)
    # The opacity of each map is in the texture alpha
    actor.SetTexture(texture)
    style_basemap(actor, mapper, offset_units)
    return actor
