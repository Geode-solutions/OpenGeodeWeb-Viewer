"""Basemap draped on the top surfaces of the georeferenced data."""

from __future__ import annotations

# Standard library imports
from typing import TYPE_CHECKING, cast

# Third party imports
import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from vtkmodules.vtkCommonCore import vtkIdList, vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPlane, vtkPolyData, vtkStaticCellLocator
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
# A surface is a piece of the topography when most of it is seen from above
MIN_VISIBLE_RATIO = 0.5
# Rays cast per surface: enough to tell a topography patch from a horizon under it
MAX_VISIBILITY_SAMPLES = 200
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


def _triangulated(surface: vtkPolyData) -> vtkPolyData:
    """The triangles of the surface only: cell ids then follow the polygons."""
    triangles = vtkTriangleFilter()
    triangles.SetInputData(surface)
    triangles.PassLinesOff()
    triangles.PassVertsOff()
    triangles.Update()
    return cast("vtkPolyData", triangles.GetOutput())


def _centroids(triangles: vtkPolyData, count: int) -> np.ndarray:
    """Centroids of up to count triangles spread over the surface: inside each triangle,
    a vertical ray never grazes an edge."""
    points = _to_numpy(triangles.GetPoints().GetData()).astype(float)
    cells = _to_numpy(triangles.GetPolys().GetConnectivityArray()).reshape(-1, 3)
    picked = cells[np.linspace(0, len(cells) - 1, min(count, len(cells))).astype(int)]
    return cast("np.ndarray", points[picked].mean(axis=1))


def upward_ratio(surface: vtkPolyData) -> float:
    """Area weighted mean of |normal z|: 1 when horizontal, 0 when vertical.

    The absolute value keeps surfaces whose normals point down.
    """
    output = _triangulated(surface)
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


def top_surfaces(surfaces: list[vtkPolyData]) -> list[vtkPolyData]:
    """Surfaces facing up and seen from above, like the pieces of a topography.

    A topography is often split in patches at very different heights: a vertical ray is cast
    from above the data through points of each surface, and the surface is kept when most
    rays meet it first. A horizon under the topography is hidden by it, however shallow.
    """
    candidates = [
        surface
        for surface in surfaces
        if surface.GetNumberOfPolys() > 0 and upward_ratio(surface) >= MIN_UPWARD_RATIO
    ]
    if not candidates:
        return []
    triangulated = [_triangulated(surface) for surface in candidates]
    append = vtkAppendPolyData()
    for triangles in triangulated:
        append.AddInputData(triangles)
    append.Update()
    merged = cast("vtkPolyData", append.GetOutput())
    # The appended cells follow the inputs: the surface of each hit cell
    owners = np.repeat(
        np.arange(len(triangulated)), [triangles.GetNumberOfPolys() for triangles in triangulated]
    )
    locator = vtkStaticCellLocator()
    locator.SetDataSet(merged)
    locator.BuildLocator()
    _, _, _, _, z_min, z_max = merged.GetBounds()
    margin = max(1.0, z_max - z_min)
    # Coincident surfaces (a patch saved twice) are both seen
    height_tolerance = 1e-6 * margin
    kept = []
    for index, (surface, triangles) in enumerate(zip(candidates, triangulated, strict=True)):
        centroids = _centroids(triangles, MAX_VISIBILITY_SAMPLES)
        visible = 0
        for x, y, z in centroids:
            hit = _first_hit(locator, (x, y, z_max + margin), (x, y, z_min - margin))
            if hit is not None and (owners[hit[0]] == index or abs(hit[1] - z) <= height_tolerance):
                visible += 1
        if visible >= MIN_VISIBLE_RATIO * len(centroids):
            kept.append(surface)
    return kept


def _first_hit(
    locator: vtkStaticCellLocator,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
) -> tuple[int, float] | None:
    """The cell met first going from start to end, and the height where it is met."""
    points = vtkPoints()
    cell_ids = vtkIdList()
    # The intersections come sorted along the line, from start to end
    locator.IntersectWithLine(start, end, 0.0, points, cell_ids)
    if cell_ids.GetNumberOfIds() == 0:
        return None
    return cell_ids.GetId(0), points.GetPoint(0)[2]


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
    drape.GetPointData().SetTCoords(probe.GetOutput().GetPointData().GetArray("basemap_uv"))
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


def clipped_to_bounds(surfaces: list[vtkPolyData], bounds: tuple[float, ...]) -> list[vtkPolyData]:
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
