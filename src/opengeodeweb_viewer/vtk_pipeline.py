# Standard library imports
from dataclasses import dataclass, field
from typing import cast, Literal, TypedDict

# Third party imports
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkMapper,
    vtkCompositePolyDataMapper,
    vtkCompositeDataDisplayAttributes,
    vtkColorTransferFunction,
)
from vtkmodules.vtkRenderingAnnotation import (
    vtkScalarBarActor,
)
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
    highlight: HighlightPipeline = field(default_factory=HighlightPipeline)
    blockDataSets: list[vtkDataObject | None] = field(default_factory=list)
    blockGeodeIds: list[str] = field(default_factory=list)
    scalarBar: vtkScalarBarActor = field(default_factory=vtkScalarBarActor)
    scalar_bars: dict[tuple, vtkScalarBarActor] = field(default_factory=dict)
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

        field_data.SetActiveScalars(style["name"])
        other_field_data.SetActiveScalars("")

        item = style.get("item", 0)
        minimum = style["minimum"]
        maximum = style["maximum"]
        points = style["points"]
        lut = create_color_transfer_function(points, minimum, maximum, item)

        if isinstance(self.mapper, vtkCompositePolyDataMapper):
            if attributes := self.mapper.GetCompositeDataDisplayAttributes():
                attributes.RemoveBlockColor(block)
        self.mapper.ScalarVisibilityOn()
        self.mapper.SetLookupTable(lut)
        self.mapper.SetScalarRange(minimum, maximum)
        self.mapper.SetColorModeToMapScalars()
        if is_point:
            self.mapper.SetScalarModeToUsePointData()
        else:
            self.mapper.SetScalarModeToUseCellData()
        self.mapper.ColorByArrayComponent(style["name"], item)
        self.mapper.InterpolateScalarsBeforeMappingOn()
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
