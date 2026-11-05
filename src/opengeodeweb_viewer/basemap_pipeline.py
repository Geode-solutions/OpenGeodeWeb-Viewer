from __future__ import annotations

# Standard library imports
from typing import TYPE_CHECKING, cast

# Third party imports
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkRenderingCore import vtkCompositePolyDataMapper

# Local application imports
from opengeodeweb_viewer.basemap_compose import basemap_texture, textures
from opengeodeweb_viewer.basemap_drape import (
    DETAIL_DRAPE_POLYGON_OFFSET_UNITS,
    clipped_to_bounds,
    drape_actor,
    drape_polydata,
    top_surfaces,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from vtkmodules.vtkRenderingCore import vtkProp, vtkRenderer

    from opengeodeweb_viewer.rpc.viewer.schemas.clipping_planes import Plane
    from opengeodeweb_viewer.vtk_pipeline import BasemapState, VtkPipeline


def compose(basemap: BasemapState, shape: tuple[int, ...]) -> None:
    full, around = textures(basemap.maps, basemap.images, basemap.layers, shape)
    basemap.full_texture = basemap_texture(full)
    # One composition for both when nothing is cropped: share its texture
    basemap.around_texture = (
        basemap.full_texture
        if around is full
        else (None if around is None else basemap_texture(around))
    )


def basemaps(
    database: Mapping[str, VtkPipeline],
) -> list[tuple[VtkPipeline, BasemapState]]:
    return [
        (pipeline, pipeline.basemap)
        for pipeline in database.values()
        if pipeline.basemap is not None
    ]


def pipeline_surfaces(pipeline: VtkPipeline) -> list[vtkPolyData]:
    """Visible surfaces of a data, after clipping, threshold, shrink and explosion."""
    if not pipeline.actor.GetVisibility():
        return []
    mapper = pipeline.mapper
    if isinstance(mapper, vtkCompositePolyDataMapper):
        attributes = mapper.GetCompositeDataDisplayAttributes()
        types = pipeline.block_component_types()
        return [
            block
            for index, block in enumerate(pipeline.block_data_sets)
            if types.get(index) == "surfaces"
            and isinstance(block, vtkPolyData)
            and attributes.GetBlockVisibility(block)
        ]
    # Solids are unstructured grids: only polydata readers hold surfaces
    if not isinstance(pipeline.reader.GetOutputDataObject(0), vtkPolyData):
        return []
    output = pipeline.filter.GetOutput()
    return [output] if output.GetNumberOfPolys() > 0 else []


def drape_planes(database: Mapping[str, VtkPipeline], basemap: BasemapState) -> list[Plane]:
    """The clipping planes of the georeferenced data the basemap lies under."""
    return next(
        (
            database[data_id].clipping_planes
            for data_id in basemap.drape_ids
            if data_id in database and database[data_id].clipping_planes
        ),
        [],
    )


def basemaps_follow(database: Mapping[str, VtkPipeline], data_ids: Iterable[str]) -> bool:
    draped = {data_id for _, basemap in basemaps(database) for data_id in basemap.drape_ids}
    # Exploded data lift the flat map, and an unknown id may be anything
    return any(
        data_id in draped
        or (pipeline := database.get(data_id)) is None
        or pipeline.basemap is not None
        or pipeline.explode_factor > 0
        for data_id in data_ids
    )


def basemap_actors(database: Mapping[str, VtkPipeline]) -> set[vtkProp]:
    """The basemap spans a margin around the data: the grid measures the data."""
    return {
        actor
        for pipeline, basemap in basemaps(database)
        for actor in (pipeline.actor, basemap.drape_actor)
        if actor is not None
    }


def update_basemaps(database: Mapping[str, VtkPipeline], renderer: vtkRenderer) -> None:
    exploded_tops = [
        pipeline.actor.GetBounds()[5]
        for pipeline in database.values()
        if pipeline.basemap is None
        and pipeline.explode_factor > 0
        and pipeline.actor.GetVisibility()
    ]
    # A detail reads what its base just drew
    for pipeline, basemap in sorted(basemaps(database), key=lambda p: p[1].detail_of is not None):
        if basemap.drape_actor is not None:
            renderer.RemoveActor(basemap.drape_actor)
            basemap.drape_actor = None
        if basemap.detail_of is None:
            _update_base(database, renderer, pipeline, exploded_tops)
        else:
            _update_detail(database, renderer, pipeline)


def _update_base(
    database: Mapping[str, VtkPipeline],
    renderer: vtkRenderer,
    pipeline: VtkPipeline,
    exploded_tops: list[float],
) -> None:
    basemap = cast("BasemapState", pipeline.basemap)
    if basemap.full_texture is None:
        return
    # Only georeferenced data: the front sends their ids
    data = [
        database[data_id]
        for data_id in basemap.drape_ids
        if data_id in database and database[data_id].actor.GetVisibility()
    ]
    draped: list[vtkPolyData] = []
    if data:
        bounds = [data_pipeline.actor.GetBounds() for data_pipeline in data]
        data_top = max(bound[5] for bound in bounds)
        z_extent = data_top - min(bound[4] for bound in bounds)
        surfaces = [
            surface for data_pipeline in data for surface in pipeline_surfaces(data_pipeline)
        ]
        draped = top_surfaces(surfaces, data_top, z_extent)
    dataset = cast("vtkPolyData", pipeline.reader.GetOutputAsDataSet())
    basemap_top = dataset.GetBounds()[5]
    if draped:
        basemap.drape_actor = drape_actor(drape_polydata(draped, dataset), basemap.full_texture)
        renderer.AddActor(basemap.drape_actor)
        # The flat map goes under the draped relief
        lift = min(surface.GetBounds()[4] for surface in draped) - basemap_top
    else:
        # Exploded blocks only move up: the flat map rises above the highest one
        lift = max([0.0, *(top - basemap_top for top in exploded_tops)])
    pipeline.actor.SetPosition(0.0, 0.0, lift)
    basemap.draped_surfaces = draped
    retexture(database, pipeline)


def _update_detail(
    database: Mapping[str, VtkPipeline], renderer: vtkRenderer, pipeline: VtkPipeline
) -> None:
    detail = cast("BasemapState", pipeline.basemap)
    base = database.get(detail.detail_of or "")
    if base is None or base.basemap is None or detail.full_texture is None:
        pipeline.actor.SetVisibility(False)  # noqa: FBT003 VTK API
        return
    dataset = cast("vtkPolyData", pipeline.reader.GetOutputAsDataSet())
    draped = clipped_to_bounds(base.basemap.draped_surfaces, dataset.GetBounds())
    if draped:
        detail.drape_actor = drape_actor(
            drape_polydata(draped, dataset),
            detail.full_texture,
            DETAIL_DRAPE_POLYGON_OFFSET_UNITS,
        )
        renderer.AddActor(detail.drape_actor)
    # Coplanar with its base: the same height, the same crop rule
    pipeline.actor.SetPosition(0.0, 0.0, base.actor.GetPosition()[2])
    retexture(database, pipeline)


def retexture(database: Mapping[str, VtkPipeline], pipeline: VtkPipeline) -> None:
    basemap = pipeline.basemap
    if basemap is None or basemap.full_texture is None:
        return
    base = database.get(basemap.detail_of or "", pipeline).basemap
    # Without draped surface, cropping would hide the whole map: the flat map shows every map
    around = basemap.around_texture
    draped = base is not None and bool(base.draped_surfaces)
    pipeline.actor.SetTexture(around if draped and around is not None else basemap.full_texture)
    # Hiding the flat map with nothing draped would hide the whole map
    flat_visible = around is not None or not draped
    pipeline.actor.SetVisibility(pipeline.visibility and flat_visible)
    if basemap.drape_actor is not None:
        basemap.drape_actor.SetTexture(basemap.full_texture)
        basemap.drape_actor.SetVisibility(pipeline.visibility)
