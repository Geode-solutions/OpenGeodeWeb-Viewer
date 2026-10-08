import logging

# Standard library imports
import math
from dataclasses import dataclass, field
from typing import Literal, TypedDict, cast

# Local application imports
from opengeodeweb_microservice.database.data_types import (
    ViewerElementsType,
    ViewerType,
)
from vtkmodules.vtkCommonDataModel import (
    vtkBoundingBox,
    vtkCompositeDataSet,
    vtkDataObject,
    vtkDataSet,
    vtkMultiBlockDataSet,
    vtkSelection,
    vtkSelectionNode,
    vtkVector2d,
)
from vtkmodules.vtkCommonExecutionModel import vtkAlgorithm
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import vtkAppendFilter, vtkThreshold
from vtkmodules.vtkFiltersExtraction import (
    vtkExtractGeometry,
    vtkExtractSelection,
)
from vtkmodules.vtkFiltersGeneral import vtkShrinkFilter, vtkTransformFilter
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkFiltersSources import vtkLineSource, vtkSphereSource
from vtkmodules.vtkIOXML import vtkXMLReader
from vtkmodules.vtkRenderingAnnotation import (
    vtkScalarBarActor,
)

# Third party imports
from vtkmodules.vtkRenderingCore import (
    VTK_SCALAR_MODE_USE_CELL_DATA,
    VTK_SCALAR_MODE_USE_POINT_DATA,
    vtkActor,
    vtkCompositeDataDisplayAttributes,
    vtkCompositePolyDataMapper,
    vtkDataSetMapper,
    vtkFollower,
    vtkMapper,
    vtkPolyDataMapper,
    vtkRenderer,
)
from vtkmodules.vtkRenderingFreeType import vtkVectorText

from opengeodeweb_viewer.utils_functions import (
    ColorClassProtocol,
    create_color_transfer_function,
)

logger = logging.getLogger(__name__)


STACKING_GAP_RATIO = 0.05


@dataclass
class ViewerData:
    id: str
    viewable_file: str | None
    viewer_object: ViewerType
    viewer_elements_type: ViewerElementsType


@dataclass
class HighlightPipeline:
    actor: vtkActor = field(default_factory=vtkActor)
    mapper: vtkDataSetMapper = field(default_factory=vtkDataSetMapper)
    selection_node: vtkSelectionNode = field(default_factory=vtkSelectionNode)
    selection: vtkSelection = field(default_factory=vtkSelection)
    extract_selection: vtkExtractSelection = field(default_factory=vtkExtractSelection)


@dataclass
class RulerPipeline:
    _SPHERE_RESOLUTION = 32
    _PRIMARY_COLOR = (60 / 255, 153 / 255, 131 / 255)
    _TEXT_COLOR = (0.05, 0.05, 0.05)

    _point1: list[float] | None = field(default=None, init=False)
    _point2: list[float] | None = field(default=None, init=False)
    _line_source: vtkLineSource = field(default_factory=vtkLineSource)
    line_actor: vtkActor = field(init=False)
    _point1_source: vtkSphereSource = field(init=False)
    point1_actor: vtkActor = field(init=False)
    _point2_source: vtkSphereSource = field(init=False)
    point2_actor: vtkActor = field(init=False)
    _text_source: vtkVectorText = field(default_factory=vtkVectorText)
    text_follower: vtkFollower = field(init=False)

    def __post_init__(self) -> None:
        self.line_actor = vtkActor()
        self._setup_actor(self.line_actor, self._line_source, self._PRIMARY_COLOR, line_width=3.0)
        self._point1_source, self.point1_actor = self._make_sphere()
        self._point2_source, self.point2_actor = self._make_sphere()
        self.text_follower = vtkFollower()
        self._setup_actor(self.text_follower, self._text_source, self._TEXT_COLOR, offset=-50000.0)

    def add_to_renderer(self, renderer: vtkRenderer) -> None:
        self.text_follower.SetCamera(renderer.GetActiveCamera())
        for actor in (
            self.line_actor,
            self.point1_actor,
            self.point2_actor,
            self.text_follower,
        ):
            actor.VisibilityOff()
            renderer.AddActor(actor)

    def _setup_actor(
        self,
        actor: vtkActor,
        source: vtkAlgorithm,
        color: tuple[float, float, float],
        line_width: float | None = None,
        offset: float = -10000.0,
    ) -> None:
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
        mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(offset, offset)
        mapper.SetRelativeCoincidentTopologyLineOffsetParameters(offset, offset)
        mapper.SetRelativeCoincidentTopologyPointOffsetParameter(offset)
        actor.SetMapper(mapper)
        actor.PickableOff()
        actor_property = actor.GetProperty()
        actor_property.SetColor(*color)
        actor_property.SetAmbient(1.0)
        actor_property.SetDiffuse(0.0)
        if line_width is not None:
            actor_property.SetLineWidth(line_width)

    def _make_sphere(self) -> tuple[vtkSphereSource, vtkActor]:
        source = vtkSphereSource()
        source.SetPhiResolution(self._SPHERE_RESOLUTION)
        source.SetThetaResolution(self._SPHERE_RESOLUTION)
        actor = vtkActor()
        self._setup_actor(actor, source, self._PRIMARY_COLOR)
        return source, actor

    def update_scale(self, renderer: vtkRenderer | None = None) -> None:
        if self._point1 is None or renderer is None:
            return
        camera_position = renderer.GetActiveCamera().GetPosition()
        self._point1_source.SetRadius(max(math.dist(self._point1, camera_position) * 0.003, 0.0001))
        if self._point2 is None:
            return
        self._point2_source.SetRadius(max(math.dist(self._point2, camera_position) * 0.003, 0.0001))
        midpoint = tuple(
            (coord1 + coord2) / 2 for coord1, coord2 in zip(self._point1, self._point2, strict=True)
        )
        text_scale = max(math.dist(midpoint, camera_position) * 0.008, 0.001)
        self.text_follower.SetPosition(midpoint[0], midpoint[1] + text_scale * 1.2, midpoint[2])
        self.text_follower.SetScale(text_scale, text_scale, text_scale)

    def reset(self) -> None:
        self._point1 = None
        self._point2 = None
        self.point1_actor.VisibilityOff()
        self.point2_actor.VisibilityOff()
        self.line_actor.VisibilityOff()
        self.text_follower.VisibilityOff()

    def set_endpoints(
        self,
        point1: list[float],
        point2: list[float] | None,
        renderer: vtkRenderer | None = None,
    ) -> float:
        self._point1 = point1
        self._point2 = point2
        self.point1_actor.VisibilityOn()
        self._point1_source.SetCenter(*point1)
        if point2 is None:
            self.point2_actor.VisibilityOff()
            self.line_actor.VisibilityOff()
            self.text_follower.VisibilityOff()
            self.update_scale(renderer)
            return 0.0
        self.point2_actor.VisibilityOn()
        self.line_actor.VisibilityOn()
        self.text_follower.VisibilityOn()
        self._line_source.SetPoint1(*point1)
        self._line_source.SetPoint2(*point2)
        self._point2_source.SetCenter(*point2)
        distance = math.dist(point1, point2)
        self._text_source.SetText(f"{distance:.2f}")
        self.update_scale(renderer)
        return distance


class BlockStyle(TypedDict):
    name: str
    attribute_location: Literal["point", "cell"]
    points: list[float]
    minimum: float
    maximum: float
    item: int
    no_data_color: ColorClassProtocol | None


@dataclass
class VtkPipeline:
    reader: vtkXMLReader
    mapper: vtkMapper
    filter: vtkGeometryFilter = field(default_factory=vtkGeometryFilter)
    actor: vtkActor = field(default_factory=vtkActor)
    slice_filter: vtkAppendFilter | None = None
    clipping_filter: vtkExtractGeometry | None = None
    threshold_filter: vtkThreshold | None = None
    shrink_filter: vtkShrinkFilter | None = None
    explode_factor: float = 0.0
    highlight: HighlightPipeline = field(default_factory=HighlightPipeline)
    block_data_sets: list[vtkDataObject | None] = field(default_factory=list)
    block_geode_ids: list[str] = field(default_factory=list)
    scalar_bar: vtkScalarBarActor = field(default_factory=vtkScalarBarActor)
    scalar_bars: dict[str, vtkScalarBarActor] = field(default_factory=dict)
    block_styles: dict[int, BlockStyle] = field(default_factory=dict)
    pick_mapper: vtkMapper | None = None

    def extract_blocks(self, multiblock: vtkDataObject | None) -> list[vtkDataObject | None]:
        if not isinstance(multiblock, vtkMultiBlockDataSet):
            return []
        blocks: list[vtkDataObject | None] = []
        iterator = multiblock.NewTreeIterator()
        iterator.InitTraversal()
        while not iterator.IsDoneWithTraversal():
            flat_index = iterator.GetCurrentFlatIndex()
            blocks.extend([None] * (flat_index + 1 - len(blocks)))
            blocks[flat_index] = iterator.GetCurrentDataObject()
            iterator.GoToNextItem()
        logger.debug(
            "[extract_blocks] Total slots=%s (None count=%s): %s",
            len(blocks),
            blocks.count(None),
            [(index, type(obj).__name__ if obj else None) for index, obj in enumerate(blocks)],
        )
        return blocks

    def prune_hidden_blocks(
        self,
        dataset: vtkMultiBlockDataSet,
        attributes: vtkCompositeDataDisplayAttributes,
    ) -> vtkMultiBlockDataSet:
        pruned = vtkMultiBlockDataSet()
        pruned.SetNumberOfBlocks(dataset.GetNumberOfBlocks())
        for index in range(dataset.GetNumberOfBlocks()):
            block = dataset.GetBlock(index)
            if block is None:
                continue
            if attributes.GetBlockVisibility(block):
                child = (
                    self.prune_hidden_blocks(block, attributes)
                    if isinstance(block, vtkMultiBlockDataSet)
                    else block
                )
                pruned.SetBlock(index, child)
        return pruned

    def source_components(self) -> dict[int, tuple[str, vtkBoundingBox]]:
        components: dict[int, tuple[str, vtkBoundingBox]] = {}
        component_type = ""
        iterator = self.reader.GetOutputDataObject(0).NewTreeIterator()
        iterator.VisitOnlyLeavesOff()
        iterator.InitTraversal()
        while not iterator.IsDoneWithTraversal():
            component = iterator.GetCurrentDataObject()
            if isinstance(component, vtkMultiBlockDataSet):
                component_type = iterator.GetCurrentMetaData().Get(vtkCompositeDataSet.NAME())
            elif isinstance(component, vtkDataSet):
                bbox = vtkBoundingBox(component.GetBounds())
                if bbox.IsValid():
                    components[iterator.GetCurrentFlatIndex()] = (component_type, bbox)
            iterator.GoToNextItem()
        return components

    @staticmethod
    def overlaps_in_xy(bbox: vtkBoundingBox, other_bbox: vtkBoundingBox) -> bool:
        return all(
            bbox.GetBound(2 * axis) < other_bbox.GetBound(2 * axis + 1)
            and other_bbox.GetBound(2 * axis) < bbox.GetBound(2 * axis + 1)
            for axis in (0, 1)
        )

    @staticmethod
    def stacking_shifts(
        stacked_blocks: dict[int, vtkBoundingBox],
    ) -> dict[int, float]:
        stacked_bbox = vtkBoundingBox()
        for bbox in stacked_blocks.values():
            stacked_bbox.AddBox(bbox)
        vertical_gap = STACKING_GAP_RATIO * stacked_bbox.GetLength(2)
        shifts: dict[int, float] = {}
        for flat_index, bbox in sorted(
            stacked_blocks.items(), key=lambda item: item[1].GetBound(4)
        ):
            shifts[flat_index] = max(
                [0.0]
                + [
                    placed_bbox.GetBound(5) + shifts[placed_index] + vertical_gap - bbox.GetBound(4)
                    for placed_index, placed_bbox in stacked_blocks.items()
                    if placed_index in shifts and VtkPipeline.overlaps_in_xy(bbox, placed_bbox)
                ]
            )
        return shifts

    @staticmethod
    def followed_shift(
        component_bbox: vtkBoundingBox,
        stacked_blocks: dict[int, vtkBoundingBox],
        stacked_shifts: dict[int, float],
    ) -> float:
        center = [0.0, 0.0, 0.0]
        component_bbox.GetCenter(center)
        containing_ids = [
            flat_index
            for flat_index, bbox in stacked_blocks.items()
            if bbox.Contains(component_bbox)
        ] or [
            flat_index for flat_index, bbox in stacked_blocks.items() if bbox.ContainsPoint(center)
        ]
        if not containing_ids:
            return 0.0
        lowest_id = min(
            containing_ids,
            key=lambda flat_index: stacked_blocks[flat_index].GetBound(4),
        )
        return stacked_shifts[lowest_id]

    def explode_blocks(self, dataset: vtkMultiBlockDataSet) -> vtkMultiBlockDataSet:
        components = self.source_components()
        stacked_blocks = {
            flat_index: bbox
            for flat_index, (component_type, bbox) in components.items()
            if component_type == "blocks"
        }
        stacked_shifts = self.stacking_shifts(stacked_blocks)
        z_shifts = {
            flat_index: (
                stacked_shifts[flat_index]
                if flat_index in stacked_shifts
                else self.followed_shift(bbox, stacked_blocks, stacked_shifts)
            )
            for flat_index, (_, bbox) in components.items()
        }
        return self.translate_blocks(dataset, z_shifts)

    def translate_blocks(
        self, dataset: vtkMultiBlockDataSet, z_shifts: dict[int, float]
    ) -> vtkMultiBlockDataSet:
        translated_dataset = vtkMultiBlockDataSet()
        translated_dataset.CopyStructure(dataset)
        iterator = dataset.NewTreeIterator()
        iterator.InitTraversal()
        while not iterator.IsDoneWithTraversal():
            block = iterator.GetCurrentDataObject()
            z_shift = z_shifts.get(iterator.GetCurrentFlatIndex(), 0.0)
            if isinstance(block, vtkDataSet) and z_shift != 0.0:
                translation = vtkTransform()
                translation.Translate(0.0, 0.0, z_shift * self.explode_factor)
                transform_filter = vtkTransformFilter()
                transform_filter.SetInputData(block)
                transform_filter.SetTransform(translation)
                transform_filter.Update()
                translated_dataset.SetDataSet(iterator, transform_filter.GetOutput())
            elif block is not None:
                translated_dataset.SetDataSet(iterator, block)
            iterator.GoToNextItem()
        translated_dataset.SetObjectName(dataset.GetObjectName())
        return translated_dataset

    def get_block_style(self, block_id: int) -> BlockStyle:
        if block_id not in self.block_styles:
            style = BlockStyle(
                name="",
                attribute_location="point",
                points=[],
                minimum=0.0,
                maximum=1.0,
                item=0,
                no_data_color=None,
            )
            self.block_styles[block_id] = style
        return self.block_styles[block_id]

    def clear_block_scalars(self, block_id: int) -> None:
        if block_id in self.block_styles:
            self.block_styles[block_id]["name"] = ""
        if block_id >= len(self.block_data_sets):
            return
        block = self.block_data_sets[block_id]
        if not isinstance(block, vtkDataSet):
            return
        block.GetPointData().SetActiveScalars("")
        block.GetCellData().SetActiveScalars("")
        if isinstance(self.mapper, vtkCompositePolyDataMapper):
            attributes = self.mapper.GetCompositeDataDisplayAttributes()
            attributes.SetBlockScalarVisibility(block, False)  # noqa: FBT003 VTK API
            attributes.RemoveBlockLookupTable(block)
            attributes.RemoveBlockArrayName(block)
            attributes.RemoveBlockArrayComponent(block)
            attributes.RemoveBlockScalarRange(block)
            attributes.RemoveBlockScalarMode(block)
            attributes.RemoveBlockInterpolateScalarsBeforeMapping(block)

    def clear_blocks_scalars(self) -> None:
        self.block_styles.clear()
        for block_id in range(len(self.block_data_sets)):
            self.clear_block_scalars(block_id)

    def update_block_colors(self, block_id: int) -> None:
        if block_id >= len(self.block_data_sets):
            return
        block = self.block_data_sets[block_id]
        if not isinstance(block, vtkDataSet):
            return
        style = self.get_block_style(block_id)
        if not style["name"]:
            self.clear_block_scalars(block_id)
            return
        is_point = style["attribute_location"] == "point"
        field_data = block.GetPointData() if is_point else block.GetCellData()
        other_field_data = block.GetCellData() if is_point else block.GetPointData()
        scalar_array = field_data.GetArray(style["name"])
        if not scalar_array:
            return
        item = style.get("item", 0)
        no_data_color = style.get("no_data_color")
        lut = create_color_transfer_function(
            style["points"], style["minimum"], style["maximum"], item, no_data_color
        )
        field_data.SetActiveScalars(style["name"])
        other_field_data.SetActiveScalars("")
        if isinstance(self.mapper, vtkCompositePolyDataMapper):
            attributes = self.mapper.GetCompositeDataDisplayAttributes()
            attributes.RemoveBlockColor(block)
            attributes.SetBlockLookupTable(block, lut)
            attributes.SetBlockArrayName(block, style["name"])
            attributes.SetBlockArrayComponent(block, item)
            attributes.SetBlockScalarRange(block, vtkVector2d(style["minimum"], style["maximum"]))
            attributes.SetBlockScalarMode(
                block,
                (VTK_SCALAR_MODE_USE_POINT_DATA if is_point else VTK_SCALAR_MODE_USE_CELL_DATA),
            )
            attributes.SetBlockInterpolateScalarsBeforeMapping(block, is_point)
            attributes.SetBlockScalarVisibility(block, True)  # noqa: FBT003 VTK API
        self.mapper.ScalarVisibilityOn()
        self.mapper.SetColorModeToMapScalars()
        self.mapper.InterpolateScalarsBeforeMappingOn()
        self.mapper.Modified()

    def sync_block_display_attributes(self, new_blocks: list[vtkDataObject | None]) -> None:
        mapper = cast("vtkCompositePolyDataMapper", self.mapper)
        attributes = mapper.GetCompositeDataDisplayAttributes()
        synced_attributes = vtkCompositeDataDisplayAttributes()
        color_rgb = [0.0, 0.0, 0.0]
        for source_block, destination_block in zip(self.block_data_sets, new_blocks, strict=False):
            if source_block and destination_block:
                if attributes.HasBlockColor(source_block):
                    attributes.GetBlockColor(source_block, color_rgb)
                    synced_attributes.SetBlockColor(destination_block, color_rgb)
                if attributes.HasBlockVisibility(source_block):
                    synced_attributes.SetBlockVisibility(
                        destination_block, attributes.GetBlockVisibility(source_block)
                    )
                if attributes.HasBlockOpacity(source_block):
                    synced_attributes.SetBlockOpacity(
                        destination_block, attributes.GetBlockOpacity(source_block)
                    )
        mapper.SetCompositeDataDisplayAttributes(synced_attributes)
        self.block_data_sets = new_blocks
        for block_id in self.block_styles:
            self.update_block_colors(block_id)

    def restore_active_scalars(self, target: vtkDataSet) -> None:
        source = self.reader.GetOutputAsDataSet()
        if active_points := source.GetPointData().GetScalars():
            target.GetPointData().SetActiveScalars(active_points.GetName())
        if active_cells := source.GetCellData().GetScalars():
            target.GetCellData().SetActiveScalars(active_cells.GetName())

    def sync_composite_pipeline(self, dataset: vtkDataObject) -> None:
        new_blocks = self.extract_blocks(dataset)
        self.sync_block_display_attributes(new_blocks)
        self.mapper.SetInputDataObject(dataset)
        if self.pick_mapper and isinstance(dataset, vtkMultiBlockDataSet):
            mapper = cast("vtkCompositePolyDataMapper", self.mapper)
            attributes = mapper.GetCompositeDataDisplayAttributes()
            self.pick_mapper.SetInputDataObject(self.prune_hidden_blocks(dataset, attributes))
