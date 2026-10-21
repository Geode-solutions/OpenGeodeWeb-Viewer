import logging

# Standard library imports
from pathlib import Path
from typing import Protocol, TypedDict, cast

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict
from vtkmodules.vtkCommonDataModel import (
    vtkBoundingBox,
    vtkCompositeDataSet,
    vtkDataSet,
    vtkMultiBlockDataSet,
)
from vtkmodules.vtkFiltersCore import vtkAppendDataSets
from vtkmodules.vtkIOXML import vtkXMLMultiBlockDataReader
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCompositeDataDisplayAttributes,
    vtkCompositePolyDataMapper,
)

# Local application imports
from opengeodeweb_viewer.object.object_methods import VtkObjectView
from opengeodeweb_viewer.typed_rpc import typed_rpc
from opengeodeweb_viewer.utils_functions import (
    AttributeProtocol,
    create_color_transfer_function,
    deterministic_color,
)
from opengeodeweb_viewer.vtk_pipeline import (
    BlockStyle,
    ModelPointsStyle,
    PointsSizeActor,
    VtkPipeline,
)

from . import schemas

logger = logging.getLogger(__name__)


class ColorProtocol(Protocol):
    red: int
    green: int
    blue: int
    alpha: float


class ColorRGBA(TypedDict):
    red: int
    green: int
    blue: int
    alpha: float


class ColorResult(TypedDict):
    viewer_id: int
    geode_id: str
    color: ColorRGBA


POINTS_COMPONENT_TYPES = ("lines", "surfaces", "blocks")


class VtkModelView(VtkObjectView):
    model_prefix = "opengeodeweb_viewer.model."
    model_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    def apply_color(
        self,
        pipeline: VtkPipeline,
        block_ids: list[int],
        color_mode: str,
        color: ColorProtocol | None = None,
        collection_id: str | None = None,
    ) -> list[ColorResult]:
        mapper = pipeline.mapper
        if not isinstance(mapper, vtkCompositePolyDataMapper):
            return []
        attr = mapper.GetCompositeDataDisplayAttributes()
        logger.debug("attr=%s", attr)
        colors: list[ColorResult] = []
        for block_id in block_ids:
            pipeline.get_block_style(block_id)
            pipeline.clear_block_scalars(block_id)
            block_dataset = pipeline.block_data_sets[block_id]
            if isinstance(block_dataset, vtkDataSet):
                if color_mode == "random":
                    geode_id = pipeline.block_geode_ids[block_id]
                    red, green, blue = deterministic_color(
                        collection_id or f"{geode_id}_{block_id}"
                    )
                    attr.SetBlockColor(block_dataset, [red, green, blue])
                    attr.SetBlockOpacity(block_dataset, 1.0)
                    colors.append(
                        {
                            "viewer_id": block_id,
                            "geode_id": str(geode_id),
                            "color": {
                                "red": round(red * 255),
                                "green": round(green * 255),
                                "blue": round(blue * 255),
                                "alpha": 1.0,
                            },
                        }
                    )
                elif color is not None:
                    red, green, blue, alpha = (
                        color.red / 255,
                        color.green / 255,
                        color.blue / 255,
                        color.alpha,
                    )
                    attr.SetBlockColor(block_dataset, [red, green, blue])
                    attr.SetBlockOpacity(block_dataset, alpha)
        mapper.Modified()
        self.setup_model_color_map(pipeline)
        return colors

    def setup_model_color_map(self, pipeline: VtkPipeline) -> None:
        # Points attributes join the polygons ones, so identical color maps share one scalar bar
        displayed_styles = [
            (str(block_id), style) for block_id, style in pipeline.block_styles.items()
        ] + [
            (f"{block_id} points", points_style.attribute)
            for block_id, points_style in pipeline.points_block_styles.items()
            if points_style.attribute is not None and points_style.visibility
        ]
        active_attrs: dict[str, BlockStyle] = {}
        for block_id, style in displayed_styles:
            if style["name"]:
                name = style["name"]
                item = style["item"]
                minimum = style["minimum"]
                maximum = style["maximum"]
                points = style["points"]
                attr_key = name
                if attr_key in active_attrs and (
                    active_attrs[attr_key]["item"] != item
                    or active_attrs[attr_key]["minimum"] != minimum
                    or active_attrs[attr_key]["maximum"] != maximum
                    or active_attrs[attr_key]["points"] != points
                ):
                    attr_key = f"{name} (Item {item + 1})" if item > 0 else name
                    if attr_key in active_attrs and (
                        active_attrs[attr_key]["minimum"] != minimum
                        or active_attrs[attr_key]["maximum"] != maximum
                        or active_attrs[attr_key]["points"] != points
                    ):
                        attr_key = f"{attr_key} [{minimum:g}, {maximum:g}]"
                        if attr_key in active_attrs and active_attrs[attr_key]["points"] != points:
                            attr_key = f"{attr_key} (Block {block_id})"
                active_attrs[attr_key] = style
        for name, style in active_attrs.items():
            if name not in pipeline.scalar_bars:
                bar = vtkScalarBarActor()
                self.get_renderer().AddViewProp(bar)
                pipeline.scalar_bars[name] = bar
            bar = pipeline.scalar_bars[name]
            item = style["item"]
            minimum = style["minimum"]
            maximum = style["maximum"]
            points = style["points"]
            no_data_color = style["no_data_color"]
            lut = create_color_transfer_function(points, minimum, maximum, item, no_data_color)
            bar.SetLookupTable(lut)
            bar.VisibilityOn()
        for name, bar in pipeline.scalar_bars.items():
            if name not in active_attrs:
                bar.VisibilityOff()

        self.update_scalar_bars_layout()

    def display_attribute_on_vertices(
        self, data_id: str, block_ids: list[int], attribute: AttributeProtocol
    ) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        for block_id in block_ids:
            style = pipeline.get_block_style(block_id)
            style["name"] = attribute.name
            style["item"] = attribute.item
            style["attribute_location"] = "point"
            style["points"] = attribute.points
            style["minimum"] = attribute.minimum
            style["maximum"] = attribute.maximum
            style["no_data_color"] = attribute.no_data_color
            pipeline.update_block_colors(block_id)
        self.setup_model_color_map(pipeline)

    def display_attribute_on_cells(
        self, data_id: str, block_ids: list[int], attribute: AttributeProtocol
    ) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        for block_id in block_ids:
            style = pipeline.get_block_style(block_id)
            style["name"] = attribute.name
            style["item"] = attribute.item
            style["attribute_location"] = "cell"
            style["points"] = attribute.points
            style["minimum"] = attribute.minimum
            style["maximum"] = attribute.maximum
            style["no_data_color"] = attribute.no_data_color
            pipeline.update_block_colors(block_id)
        self.setup_model_color_map(pipeline)

    def setup_color_map(
        self,
        pipeline: VtkPipeline,
        block_ids: list[int],
        points: list[float],
        minimum: float,
        maximum: float,
    ) -> None:
        for block_id in block_ids:
            style = pipeline.get_block_style(block_id)
            style["points"] = points
            style["minimum"] = minimum
            style["maximum"] = maximum
            pipeline.update_block_colors(block_id)
        self.setup_model_color_map(pipeline)

    def ensure_model_points_styles(self, pipeline: VtkPipeline) -> dict[int, ModelPointsStyle]:
        # Components points leave the main actor once styled individually
        if pipeline.points_block_styles:
            return pipeline.points_block_styles
        main_property = pipeline.actor.GetProperty()
        for block_id, component_type in pipeline.block_component_types().items():
            if component_type in POINTS_COMPONENT_TYPES:
                pipeline.points_block_styles[block_id] = ModelPointsStyle(
                    size=main_property.GetPointSize(),
                    visibility=bool(main_property.GetVertexVisibility()),
                )
        main_property.VertexVisibilityOff()
        return pipeline.points_block_styles

    def sync_points_size_actors(self, pipeline: VtkPipeline) -> None:
        renderer = self.get_renderer()
        sizes = {style.size for style in pipeline.points_block_styles.values()}
        for size in list(pipeline.points_size_actors):
            if size not in sizes:
                renderer.RemoveActor(pipeline.points_size_actors.pop(size).actor)
        main_property = pipeline.actor.GetProperty()
        for size in sizes - pipeline.points_size_actors.keys():
            mapper = vtkCompositePolyDataMapper()
            mapper.SetInputDataObject(pipeline.mapper.GetInputDataObject(0, 0))
            mapper.ScalarVisibilityOn()
            mapper.SetColorModeToMapScalars()
            mapper.SetResolveCoincidentTopologyPointOffsetParameter(-2)
            actor = vtkActor()
            actor.SetMapper(mapper)
            actor.PickableOff()
            actor.SetVisibility(pipeline.actor.GetVisibility())
            points_property = actor.GetProperty()
            points_property.SetRepresentationToPoints()
            points_property.SetPointSize(size)
            points_property.SetColor(*main_property.GetVertexColor())
            pipeline.points_size_actors[size] = PointsSizeActor(mapper=mapper, actor=actor)
        # Bigger points are drawn first so smaller coincident ones stay visible on top
        for size in sorted(pipeline.points_size_actors, reverse=True):
            renderer.RemoveActor(pipeline.points_size_actors[size].actor)
            renderer.AddActor(pipeline.points_size_actors[size].actor)
        pipeline.update_points_size_actors()

    def component_points_styles(
        self, data_id: str, component_type: str, block_ids: list[int]
    ) -> list[ModelPointsStyle]:
        pipeline = self.get_vtk_pipeline(data_id)
        styles = self.ensure_model_points_styles(pipeline)
        component_types = pipeline.block_component_types()
        return [
            styles[block_id]
            for block_id in block_ids
            if block_id in styles and component_types.get(block_id) == component_type
        ]

    def set_component_points_visibility(
        self, data_id: str, component_type: str, block_ids: list[int], *, visibility: bool
    ) -> None:
        for style in self.component_points_styles(data_id, component_type, block_ids):
            style.visibility = visibility
        pipeline = self.get_vtk_pipeline(data_id)
        self.sync_points_size_actors(pipeline)
        self.setup_model_color_map(pipeline)

    def set_component_points_color(
        self, data_id: str, component_type: str, block_ids: list[int], color: ColorProtocol
    ) -> None:
        for style in self.component_points_styles(data_id, component_type, block_ids):
            style.color = (color.red / 255, color.green / 255, color.blue / 255)
            style.opacity = color.alpha
            style.attribute = None
        pipeline = self.get_vtk_pipeline(data_id)
        self.sync_points_size_actors(pipeline)
        self.setup_model_color_map(pipeline)

    def set_component_points_attribute(
        self,
        data_id: str,
        component_type: str,
        block_ids: list[int],
        attribute: AttributeProtocol,
    ) -> None:
        for style in self.component_points_styles(data_id, component_type, block_ids):
            style.attribute = BlockStyle(
                name=attribute.name,
                attribute_location="point",
                points=attribute.points,
                minimum=attribute.minimum,
                maximum=attribute.maximum,
                item=attribute.item,
                no_data_color=attribute.no_data_color,
            )
        pipeline = self.get_vtk_pipeline(data_id)
        self.sync_points_size_actors(pipeline)
        self.setup_model_color_map(pipeline)

    def set_component_points_size(
        self, data_id: str, component_type: str, block_ids: list[int], size: float
    ) -> None:
        for style in self.component_points_styles(data_id, component_type, block_ids):
            style.size = size
        self.sync_points_size_actors(self.get_vtk_pipeline(data_id))

    def set_model_points_visibility_on_all(self, data_id: str, *, visibility: bool) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        if not pipeline.points_block_styles:
            self.set_points_visibility(data_id, visibility=visibility)
            return
        for style in pipeline.points_block_styles.values():
            style.visibility = visibility
        self.sync_points_size_actors(pipeline)
        self.setup_model_color_map(pipeline)

    def set_model_points_size_on_all(self, data_id: str, size: float) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        self.set_points_size(data_id, size)
        for style in pipeline.points_block_styles.values():
            style.size = size
        self.sync_points_size_actors(pipeline)

    @typed_rpc(model_prefix, schemas.register_route)
    def register_model(self, params: schemas.Register) -> schemas.RegisterResponse:
        data_id = params.id
        try:
            viewer_data = self.get_viewer_data(data_id)
            file_name = str(viewer_data.viewable_file)

            reader = vtkXMLMultiBlockDataReader()
            reader.SetFileName(str(Path(self.DATA_FOLDER_PATH) / data_id / file_name))
            reader.Update()
            mapper = vtkCompositePolyDataMapper()
            attributes = vtkCompositeDataDisplayAttributes()
            mapper.SetCompositeDataDisplayAttributes(attributes)
            data = VtkPipeline(reader, mapper)
            geometry_output = cast("vtkMultiBlockDataSet", self.setup_pipeline(data, params.name))
            self.highlight(data)
            iterator = geometry_output.NewTreeIterator()
            iterator.InitTraversal()
            while not iterator.IsDoneWithTraversal():
                block = iterator.GetCurrentDataObject()
                if block is not None:
                    flat_index = iterator.GetCurrentFlatIndex()
                    while flat_index > len(data.block_data_sets):
                        data.block_data_sets.append(None)
                        data.block_geode_ids.append("")
                    data.block_data_sets.append(block)
                    meta = iterator.GetCurrentMetaData()
                    name = meta.Get(vtkCompositeDataSet.NAME())
                    data.block_geode_ids.append(name)
                iterator.GoToNextItem()
            self.add_object(data_id, data)
        except Exception:
            logger.exception("Error registering model %s", data_id)
            raise
        return schemas.RegisterResponse()

    @typed_rpc(model_prefix, schemas.deregister_route)
    def deregister_model(self, params: schemas.Deregister) -> schemas.DeregisterResponse:
        self.remove_object(params.id)
        return schemas.DeregisterResponse()

    @typed_rpc(model_prefix, schemas.visibility_route)
    def set_model_visibility(self, params: schemas.Visibility) -> schemas.VisibilityResponse:
        self.set_visibility(params.id, visibility=params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(model_prefix, schemas.highlight_route)
    def set_model_highlight(self, params: schemas.Highlight) -> schemas.HighlightResponse:
        pipeline = self.get_vtk_pipeline(params.id)
        if params.visibility and params.block_ids:
            append = vtkAppendDataSets()
            for i in params.block_ids:
                block = pipeline.block_data_sets[i] if i < len(pipeline.block_data_sets) else None
                if isinstance(block, vtkDataSet):
                    append.AddInputData(block)
            append.Update()
            pipeline.highlight.mapper.SetInputDataObject(append.GetOutput())
        else:
            pipeline.highlight.mapper.SetInputConnection(
                pipeline.highlight.extract_selection.GetOutputPort()
            )
        pipeline.highlight.actor.SetVisibility(params.visibility)
        self.render(-1)
        return schemas.HighlightResponse()

    @typed_rpc(model_prefix, schemas.get_blocks_bounds_route)
    def get_blocks_bounds(self, params: schemas.GetBlocksBounds) -> schemas.GetBlocksBoundsResponse:
        pipeline = self.get_vtk_pipeline(params.id)
        bbox = vtkBoundingBox()
        for block_id in params.block_ids:
            if isinstance(block := pipeline.block_data_sets[block_id], vtkDataSet):
                bbox.AddBounds(block.GetBounds())

        bounds = [0.0] * 6
        bbox.GetBounds(bounds)
        return schemas.GetBlocksBoundsResponse(bounds=bounds)
