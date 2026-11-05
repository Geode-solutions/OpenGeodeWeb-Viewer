import logging

# Standard library imports
from pathlib import Path
from typing import TYPE_CHECKING

from opengeodeweb_microservice.database.data import Data

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict
from vtkmodules.vtkIOXML import vtkXMLGenericDataObjectReader, vtkXMLImageDataReader
from vtkmodules.vtkRenderingCore import (
    vtkDataSetMapper,
    vtkTexture,
)

# Local application imports
from opengeodeweb_viewer.basemap_compose import mosaic, read_tiles
from opengeodeweb_viewer.basemap_drape import (
    BASEMAP_POLYGON_OFFSET_UNITS,
    DETAIL_POLYGON_OFFSET_UNITS,
    style_basemap,
)
from opengeodeweb_viewer.basemap_pipeline import compose, retexture
from opengeodeweb_viewer.object.object_methods import VtkObjectView
from opengeodeweb_viewer.typed_rpc import typed_rpc
from opengeodeweb_viewer.utils_functions import (
    AttributeProtocol,
    create_color_transfer_function,
)
from opengeodeweb_viewer.vtk_pipeline import BasemapState, ColorMapKey, VtkPipeline

from . import schemas

if TYPE_CHECKING:
    from collections.abc import Mapping

    from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor

    from opengeodeweb_viewer.basemap_compose import LayerState

logger = logging.getLogger(__name__)

DEFAULT_TILE_SIZE = 256
# The Back writes the tiles of every source in this folder of the basemap data
TILES_FOLDER = "tiles"


def check_source_folder(name: str) -> None:
    """A source folder is a folder of the tiles, never a path out of them."""
    if name in ("", ".", "..") or "/" in name or "\\" in name:
        msg = f"Invalid basemap source {name!r}: expected a plain folder name"
        raise ValueError(msg)


def _state_values(
    states: Mapping[str, LayerState],
) -> dict[str, tuple[bool, float, bool]]:
    return {name: (state.visible, state.opacity, state.crop) for name, state in states.items()}


class VtkMeshView(VtkObjectView):
    mesh_prefix = "opengeodeweb_viewer.mesh."
    mesh_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_prefix, schemas.register_route)
    def register_mesh(self, params: schemas.Register) -> schemas.RegisterResponse:
        logger.debug("%s", self.mesh_schemas_dict["register"])
        data_id = params.id
        try:
            viewer_data = self.get_viewer_data(data_id)
            file_name = str(viewer_data.viewable_file)

            reader = vtkXMLGenericDataObjectReader()
            reader.SetFileName(str(Path(self.DATA_FOLDER_PATH) / data_id / file_name))
            reader.Update()
            mapper = vtkDataSetMapper()
            data = VtkPipeline(reader, mapper)
            self.setup_pipeline(data, params.name)
            self.highlight(data)
            self.add_object(data_id, data)
        except Exception:
            logger.exception("Error registering mesh %s", data_id)
            raise
        return schemas.RegisterResponse()

    @typed_rpc(mesh_prefix, schemas.deregister_route)
    def deregister_mesh(self, params: schemas.Deregister) -> schemas.DeregisterResponse:
        self.remove_object(params.id)
        return schemas.DeregisterResponse()

    @typed_rpc(mesh_prefix, schemas.visibility_route)
    def set_mesh_visibility(self, params: schemas.Visibility) -> schemas.VisibilityResponse:
        self.set_visibility(params.id, visibility=params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(mesh_prefix, schemas.color_route)
    def set_mesh_color(self, params: schemas.Color) -> schemas.ColorResponse:
        color = params.color
        self.set_color(params.id, color)
        return schemas.ColorResponse()

    @typed_rpc(mesh_prefix, schemas.apply_textures_route)
    def mesh_apply_textures(self, params: schemas.ApplyTextures) -> schemas.ApplyTexturesResponse:
        mesh_id = params.id
        for tex_info in params.textures:
            texture_id = tex_info.id
            texture_data = Data.get(texture_id)
            if texture_data is None:
                continue
            texture_file = texture_data.viewable_file
            if texture_file is None or not texture_file.lower().endswith(".vti"):
                continue
            texture_file_path = self.get_data_file_path(texture_id)
            texture_reader = vtkXMLImageDataReader()
            texture_reader.SetFileName(texture_file_path)
            texture_reader.Update()
            texture = vtkTexture()
            texture.SetInputConnection(texture_reader.GetOutputPort())
            texture.InterpolateOn()
            pipeline = self.get_vtk_pipeline(mesh_id)
            output = pipeline.reader.GetOutputAsDataSet()
            array = output.GetPointData().GetArray(tex_info.texture_name)
            if array:
                output.GetPointData().SetTCoords(array)
            pipeline.filter.Modified()
            pipeline.filter.Update()
            pipeline.actor.SetTexture(texture)
        return schemas.ApplyTexturesResponse()

    @typed_rpc(mesh_prefix, schemas.apply_basemap_route)
    def mesh_apply_basemap(self, params: schemas.ApplyBasemap) -> schemas.ApplyBasemapResponse:
        folder = Path(self.get_data_file_path(params.id, TILES_FOLDER))
        pipeline = self.get_vtk_pipeline(params.id)
        maps = [(entry.map, list(entry.sources)) for entry in params.maps]
        sources = [source for _, names in maps for source in names]
        for source in sources:
            check_source_folder(source)
        tiles = {source: read_tiles(folder / source) for source in sources}
        # The mosaics are stacked pixel on pixel: every tile must have the same size
        sizes = {
            tile.shape[:2] for source_tiles in tiles.values() for tile in source_tiles.values()
        }
        if len(sizes) > 1:
            msg = f"Basemap tiles of different sizes: {sorted(sizes)}"
            raise ValueError(msg)
        tile_shape = sizes.pop() if sizes else (DEFAULT_TILE_SIZE, DEFAULT_TILE_SIZE)
        # Built whole before it replaces the previous one: an invalid folder leaves it as it was
        basemap = BasemapState(
            maps=maps,
            images={
                source: mosaic(source_tiles, params.columns, params.rows, tile_shape)
                for source, source_tiles in tiles.items()
            },
            layers={layer.map: layer for layer in params.layers},
            detail_of=params.detail_of,
        )
        compose(basemap, (params.rows * tile_shape[0], params.columns * tile_shape[1]))
        output = pipeline.reader.GetOutputAsDataSet()
        output.GetPointData().SetTCoords(output.GetPointData().GetArray("basemap_uv"))
        pipeline.filter.Modified()
        pipeline.filter.Update()
        style_basemap(
            pipeline.actor,
            pipeline.mapper,
            (
                BASEMAP_POLYGON_OFFSET_UNITS
                if params.detail_of is None
                else DETAIL_POLYGON_OFFSET_UNITS
            ),
        )
        if pipeline.basemap is not None:
            basemap.drape_ids = pipeline.basemap.drape_ids
            basemap.drape_actor = pipeline.basemap.drape_actor
        pipeline.basemap = basemap
        # A basemap rebuilt while the data is clipped or exploded follows it at once
        self.clip_basemap(pipeline)
        self.mark_basemaps_dirty()
        return schemas.ApplyBasemapResponse()

    @typed_rpc(mesh_prefix, schemas.basemap_layers_route)
    def mesh_basemap_layers(self, params: schemas.BasemapLayers) -> schemas.BasemapLayersResponse:
        pipeline = self.get_vtk_pipeline(params.id)
        basemap = pipeline.basemap
        # Before apply_basemap there is no image to compose
        if basemap is None:
            return schemas.BasemapLayersResponse()
        layers: dict[str, LayerState] = {layer.map: layer for layer in params.layers}
        # The same states again: the textures already show them
        if _state_values(layers) == _state_values(basemap.layers):
            return schemas.BasemapLayersResponse()
        basemap.layers = layers
        if basemap.images:
            compose(basemap, next(iter(basemap.images.values())).shape[:2])
            # Same geometry: the existing actors only get the new textures
            retexture(self.get_data_base(), pipeline)
        return schemas.BasemapLayersResponse()

    @typed_rpc(mesh_prefix, schemas.basemap_drape_route)
    def mesh_basemap_drape(self, params: schemas.BasemapDrape) -> schemas.BasemapDrapeResponse:
        pipeline = self.get_vtk_pipeline(params.id)
        if pipeline.basemap is None:
            msg = f"Data {params.id} is not a basemap: apply_basemap first"
            raise ValueError(msg)
        pipeline.basemap.drape_ids = list(params.data_ids)
        # Cut like the data it now lies under
        self.clip_basemap(pipeline)
        self.mark_basemaps_dirty()
        return schemas.BasemapDrapeResponse()

    def display_attribute_on_vertices(self, data_id: str, attribute: AttributeProtocol) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        name = attribute.name
        pipeline.reader.GetOutputAsDataSet().GetPointData().SetActiveScalars(name)
        pipeline.filter.Update()
        if active_ds := pipeline.mapper.GetInputDataObject(0, 0):
            active_ds.GetPointData().SetActiveScalars(name)
        pipeline.mapper.ScalarVisibilityOn()
        pipeline.mapper.SetScalarModeToUsePointData()
        pipeline.mapper.ColorByArrayComponent(name, attribute.item)
        self.setup_color_map(data_id, attribute)

    def display_attribute_on_points(self, data_id: str, attribute: AttributeProtocol) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        self.ensure_points_actor(pipeline)
        if pipeline.points_mapper is None:
            return
        pipeline.points_color_map_key = self.display_attribute_on_style_mapper(
            pipeline.points_mapper, pipeline.points_scalar_bar, attribute
        )
        self.update_style_scalar_bars_visibility(pipeline)
        self.update_scalar_bars_layout()

    def display_attribute_on_edges(self, data_id: str, attribute: AttributeProtocol) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        self.ensure_edges_actor(pipeline)
        if pipeline.edges_mapper is None:
            return
        pipeline.edges_color_map_key = self.display_attribute_on_style_mapper(
            pipeline.edges_mapper, pipeline.edges_scalar_bar, attribute
        )
        self.update_style_scalar_bars_visibility(pipeline)
        self.update_scalar_bars_layout()

    def display_attribute_on_style_mapper(
        self,
        mapper: vtkDataSetMapper,
        scalar_bar: vtkScalarBarActor | None,
        attribute: AttributeProtocol,
    ) -> ColorMapKey:
        # Field data mode avoids touching the active scalars shared with the polygons
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointFieldData()
        mapper.ColorByArrayComponent(attribute.name, attribute.item)
        lut = create_color_transfer_function(
            attribute.points,
            attribute.minimum,
            attribute.maximum,
            attribute.item,
            attribute.no_data_color,
        )
        lut.SetRange(attribute.minimum, attribute.maximum)
        mapper.SetLookupTable(lut)
        mapper.SetScalarRange(attribute.minimum, attribute.maximum)
        mapper.UseLookupTableScalarRangeOff()
        mapper.InterpolateScalarsBeforeMappingOn()
        # Whether this bar shows or reuses an identical one is decided on each visibility update
        if scalar_bar is not None:
            scalar_bar.SetLookupTable(lut)
        return (
            attribute.name,
            attribute.item,
            attribute.minimum,
            attribute.maximum,
            tuple(attribute.points),
        )

    def display_attribute_on_cells(self, data_id: str, attribute: AttributeProtocol) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        name = attribute.name
        pipeline.reader.GetOutputAsDataSet().GetCellData().SetActiveScalars(name)
        pipeline.filter.Update()
        if active_ds := pipeline.mapper.GetInputDataObject(0, 0):
            active_ds.GetCellData().SetActiveScalars(name)
        pipeline.mapper.ScalarVisibilityOn()
        pipeline.mapper.SetScalarModeToUseCellData()
        pipeline.mapper.ColorByArrayComponent(name, attribute.item)
        self.setup_color_map(data_id, attribute)

    def display_scalar_range(self, data_id: str, minimum: float, maximum: float) -> None:
        logger.debug("Setting scalar range for %s to (%s, %s)", data_id, minimum, maximum)
        data = self.get_vtk_pipeline(data_id)
        data.mapper.SetScalarRange(minimum, maximum)
        data.mapper.GetLookupTable().SetRange(minimum, maximum)
        data.mapper.UseLookupTableScalarRangeOff()
        self.update_style_scalar_bars_visibility(data)
        self.update_scalar_bars_layout()

    def setup_color_map(self, data_id: str, attribute: AttributeProtocol) -> None:
        data = self.get_vtk_pipeline(data_id)
        minimum = attribute.minimum
        maximum = attribute.maximum
        lut = create_color_transfer_function(
            attribute.points, minimum, maximum, attribute.item, attribute.no_data_color
        )
        data.mapper.SetLookupTable(lut)
        data.color_map_points = list(attribute.points)

        data.mapper.SetScalarRange(minimum, maximum)
        lut.SetRange(minimum, maximum)
        data.mapper.UseLookupTableScalarRangeOff()
        data.mapper.InterpolateScalarsBeforeMappingOn()

        data.scalar_bar.SetLookupTable(lut)
        data.scalar_bar.VisibilityOn()
        self.update_style_scalar_bars_visibility(data)
        self.update_scalar_bars_layout()

    @typed_rpc(mesh_prefix, schemas.highlight_route)
    def set_mesh_highlight(self, params: schemas.Highlight) -> schemas.HighlightResponse:
        pipeline = self.get_vtk_pipeline(params.id)
        if params.visibility:
            dataset = pipeline.reader.GetOutputDataObject(0)
            pipeline.highlight.mapper.SetInputDataObject(dataset)
        else:
            pipeline.highlight.mapper.SetInputConnection(
                pipeline.highlight.extract_selection.GetOutputPort()
            )
        pipeline.highlight.actor.SetVisibility(params.visibility)
        self.render(-1)
        return schemas.HighlightResponse()
