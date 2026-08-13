# Standard library imports
from dataclasses import dataclass, field
import math
from typing import cast, Literal, TypedDict

# Third party imports
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkFollower,
    vtkMapper,
    vtkPolyDataMapper,
    vtkCompositePolyDataMapper,
    vtkCompositeDataDisplayAttributes,
    vtkColorTransferFunction,
)
from vtkmodules.vtkRenderingAnnotation import (
    vtkScalarBarActor,
)
from vtkmodules.vtkRenderingFreeType import vtkVectorText
from vtkmodules.vtkFiltersSources import vtkLineSource, vtkSphereSource
from vtkmodules.vtkCommonDataModel import (
    vtkDataObject,
    vtkDataSet,
    vtkMultiBlockDataSet,
    vtkSelection,
    vtkSelectionNode,
)
from vtkmodules.vtkCommonExecutionModel import vtkAlgorithm
from vtkmodules.vtkFiltersExtraction import (
    vtkExtractGeometry,
    vtkExtractSelection,
)
from vtkmodules.vtkFiltersGeneral import vtkShrinkFilter
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkIOXML import vtkXMLReader

# Local application imports
from opengeodeweb_microservice.database.data_types import (
    ViewerElementsType,
    ViewerType,
)
from opengeodeweb_viewer.utils_functions import create_color_transfer_function


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
    selectionNode: vtkSelectionNode = field(default_factory=vtkSelectionNode)
    selection: vtkSelection = field(default_factory=vtkSelection)
    extractSelection: vtkExtractSelection = field(default_factory=vtkExtractSelection)

@dataclass
class RulerPipeline:
    _SPHERE_RESOLUTION = 32
    _PRIMARY_COLOR = (60 / 255, 153 / 255, 131 / 255)
    _TEXT_COLOR = (0.05, 0.05, 0.05)

    _point1: tuple[float, float, float] | None = field(default=None, init=False)
    _point2: tuple[float, float, float] | None = field(default=None, init=False)
    _line_source: vtkLineSource = field(default_factory=vtkLineSource)
    line_actor: vtkActor = field(init=False)
    _point1_source: vtkSphereSource = field(init=False)
    point1_actor: vtkActor = field(init=False)
    _point2_source: vtkSphereSource = field(init=False)
    point2_actor: vtkActor = field(init=False)
    _text_source: vtkVectorText = field(default_factory=vtkVectorText)
    text_follower: vtkFollower = field(init=False)

    def __post_init__(self) -> None:
        self.line_actor = self._setup_actor(
            vtkActor(), self._line_source, self._PRIMARY_COLOR, line_width=3.0
        )
        self._point1_source, self.point1_actor = self._make_sphere()
        self._point2_source, self.point2_actor = self._make_sphere()
        self.text_follower = self._setup_actor(
            vtkFollower(), self._text_source, self._TEXT_COLOR, offset=-50000.0
        )

    def add_to_renderer(self, renderer) -> None:
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
        actor,
        source,
        color: tuple[float, float, float],
        line_width: float | None = None,
        offset: float = -10000.0,
    ):
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
        mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(offset, offset)
        mapper.SetRelativeCoincidentTopologyLineOffsetParameters(offset, offset)
        mapper.SetRelativeCoincidentTopologyPointOffsetParameter(offset)
        actor.SetMapper(mapper)
        actor.SetPickable(False)
        actor_property = actor.GetProperty()
        actor_property.SetColor(*color)
        actor_property.SetAmbient(1.0)
        actor_property.SetDiffuse(0.0)
        if line_width is not None:
            actor_property.SetLineWidth(line_width)
        return actor

    def _make_sphere(self) -> tuple[vtkSphereSource, vtkActor]:
        source = vtkSphereSource()
        source.SetPhiResolution(self._SPHERE_RESOLUTION)
        source.SetThetaResolution(self._SPHERE_RESOLUTION)
        return source, self._setup_actor(vtkActor(), source, self._PRIMARY_COLOR)

    def update_scale(self, renderer=None) -> None:
        if self._point1 is None or renderer is None:
            return
        camera_position = renderer.GetActiveCamera().GetPosition()
        self._point1_source.SetRadius(
            max(math.dist(self._point1, camera_position) * 0.003, 0.0001)
        )
        if self._point2 is None:
            return
        self._point2_source.SetRadius(
            max(math.dist(self._point2, camera_position) * 0.003, 0.0001)
        )
        midpoint = tuple(
            (coord1 + coord2) / 2
            for coord1, coord2 in zip(self._point1, self._point2)
        )
        text_scale = max(math.dist(midpoint, camera_position) * 0.008, 0.001)
        self.text_follower.SetPosition(
            midpoint[0], midpoint[1] + text_scale * 1.2, midpoint[2]
        )
        self.text_follower.SetScale(text_scale, text_scale, text_scale)

    def set_endpoints(
        self,
        point1: tuple[float, float, float] | None,
        point2: tuple[float, float, float] | None,
        renderer=None,
    ) -> float:
        self._point1 = point1
        self._point2 = point2
        self.point1_actor.SetVisibility(point1 is not None)
        self.point2_actor.SetVisibility(point2 is not None)
        self.line_actor.SetVisibility(point2 is not None)
        self.text_follower.SetVisibility(point2 is not None)
        if point1 is not None:
            self._point1_source.SetCenter(*point1)
        if point2 is None or point1 is None:
            self.update_scale(renderer)
            return 0.0
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


@dataclass
class VtkPipeline:
    reader: vtkXMLReader
    mapper: vtkMapper
    filter: vtkGeometryFilter = field(default_factory=vtkGeometryFilter)
    actor: vtkActor = field(default_factory=vtkActor)
    clipping_filter: vtkExtractGeometry | None = None
    shrink_filter: vtkShrinkFilter | None = None
    highlight: HighlightPipeline = field(default_factory=HighlightPipeline)
    blockDataSets: list[vtkDataObject | None] = field(default_factory=list)
    blockGeodeIds: list[str] = field(default_factory=list)
    scalarBar: vtkScalarBarActor = field(default_factory=vtkScalarBarActor)
    scalar_bars: dict[str, vtkScalarBarActor] = field(default_factory=dict)
    block_styles: dict[int, BlockStyle] = field(default_factory=dict)
    pick_mapper: vtkMapper | None = None

    def extract_blocks(
        self, multiblock: vtkDataObject | None
    ) -> list[vtkDataObject | None]:
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
        print(
            f"[extract_blocks] Total slots={len(blocks)} (None count={blocks.count(None)}): "
            f"{[(index, type(obj).__name__ if obj else None) for index, obj in enumerate(blocks)]}",
            flush=True,
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
            if block and attributes.GetBlockVisibility(block):
                child = (
                    self.prune_hidden_blocks(block, attributes)
                    if isinstance(block, vtkMultiBlockDataSet)
                    else block
                )
                pruned.SetBlock(index, child)
        return pruned

    def get_block_style(self, block_id: int) -> BlockStyle:
        if block_id not in self.block_styles:
            style = BlockStyle(
                name="",
                attribute_location="point",
                points=[],
                minimum=0.0,
                maximum=1.0,
                item=0,
            )
            self.block_styles[block_id] = style
        return self.block_styles[block_id]

    def update_block_colors(self, block_id: int) -> None:
        block = self.blockDataSets[block_id]
        if not isinstance(block, vtkDataSet):
            return
        style = self.get_block_style(block_id)
        if not style["name"]:
            block.GetPointData().SetActiveScalars("")
            block.GetCellData().SetActiveScalars("")
            return
        is_point = style["attribute_location"] == "point"
        field_data = block.GetPointData() if is_point else block.GetCellData()
        other_field_data = block.GetCellData() if is_point else block.GetPointData()
        scalar_array = field_data.GetArray(style["name"])
        if not scalar_array:
            return
        item = style.get("item", 0)
        lut = create_color_transfer_function(
            style["points"], style["minimum"], style["maximum"], item
        )
        rgba_colors = lut.MapScalars(scalar_array, 1, item)
        rgba_colors.SetName(f"__colors_{style['name']}")
        field_data.AddArray(rgba_colors)
        field_data.SetActiveScalars(rgba_colors.GetName())
        other_field_data.SetActiveScalars("")
        if isinstance(self.mapper, vtkCompositePolyDataMapper):
            if attributes := self.mapper.GetCompositeDataDisplayAttributes():
                attributes.RemoveBlockColor(block)
        self.mapper.ScalarVisibilityOn()
        self.mapper.SetColorModeToDirectScalars()
        self.mapper.SetScalarModeToDefault()
        self.mapper.Modified()

    def sync_block_display_attributes(
        self, new_blocks: list[vtkDataObject | None]
    ) -> None:
        mapper = cast(vtkCompositePolyDataMapper, self.mapper)
        attributes = mapper.GetCompositeDataDisplayAttributes()
        color_rgb = [0.0, 0.0, 0.0]
        for source_block, destination_block in zip(self.blockDataSets, new_blocks):
            if source_block and destination_block:
                if attributes.HasBlockColor(source_block):
                    attributes.GetBlockColor(source_block, color_rgb)
                    attributes.SetBlockColor(destination_block, color_rgb)
                else:
                    attributes.RemoveBlockColor(destination_block)
                if attributes.HasBlockVisibility(source_block):
                    attributes.SetBlockVisibility(
                        destination_block, attributes.GetBlockVisibility(source_block)
                    )
                if attributes.HasBlockOpacity(source_block):
                    attributes.SetBlockOpacity(
                        destination_block, attributes.GetBlockOpacity(source_block)
                    )
        self.blockDataSets = new_blocks
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
            mapper = cast(vtkCompositePolyDataMapper, self.mapper)
            attributes = mapper.GetCompositeDataDisplayAttributes()
            self.pick_mapper.SetInputDataObject(
                self.prune_hidden_blocks(dataset, attributes)
            )
