# Standard library imports
import math
import os
from typing import cast, Any, Literal, TypedDict
from dataclasses import dataclass, field

# Third party imports
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.web import protocols as vtk_protocols
from vtkmodules.vtkIOXML import (
    vtkXMLReader,
)
from vtkmodules.vtkWebCore import vtkWebApplication
from vtkmodules.vtkCommonExecutionModel import (
    vtkAlgorithm,
    vtkCompositeDataPipeline,
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkDataSetMapper,
    vtkCompositePolyDataMapper,
    vtkCompositeDataDisplayAttributes,
    vtkCellPicker,
    vtkHardwarePicker,
    vtkColorTransferFunction,
)
from vtkmodules.vtkCommonDataModel import (
    vtkDataObject,
    vtkDataSet,
    vtkMultiBlockDataSet,
    vtkBoundingBox,
    vtkSelection,
    vtkSelectionNode,
    vtkPlane,
    vtkImplicitBoolean,
)
from vtkmodules.vtkFiltersExtraction import (
    vtkExtractSelection,
    vtkExtractGeometry,
)
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkCommonCore import vtkStringArray, vtkIdTypeArray
from vtkmodules.vtkRenderingAnnotation import (
    vtkCubeAxesActor,
    vtkAxesActor,
    vtkScalarBarActor,
)
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget

# Local application imports
from opengeodeweb_microservice.database.connection import get_session, init_database
from opengeodeweb_microservice.database.data import Data
from opengeodeweb_microservice.database.data_types import ViewerType, ViewerElementsType
from opengeodeweb_viewer.rpc.viewer.schemas.clipping_planes import Plane


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
    filter: vtkAlgorithm | None = None
    actor: vtkActor = field(default_factory=vtkActor)
    clipping_filter: vtkExtractGeometry | None = None
    highlight: HighlightPipeline = field(default_factory=HighlightPipeline)
    blockDataSets: list[vtkDataObject | None] = field(default_factory=list)
    blockGeodeIds: list[str] = field(default_factory=list)
    scalarBar: vtkScalarBarActor = field(default_factory=vtkScalarBarActor)
    block_styles: dict[int, BlockStyle] = field(default_factory=dict)
    pick_mapper: vtkMapper | None = None


class VtkTypingMixin:
    def getView(self, view_id: str) -> vtkRenderWindow:
        return cast(vtkRenderWindow, super().getView(view_id))  # type: ignore

    def registerVtkWebProtocol(self, protocol: Any) -> None:
        super().registerVtkWebProtocol(protocol)  # type: ignore

    def getApplication(self) -> vtkWebApplication:
        return cast(vtkWebApplication, super().getApplication())  # type: ignore


class VtkView(VtkTypingMixin, vtk_protocols.vtkWebProtocol):
    def __init__(self) -> None:
        super().__init__()
        self.DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH", ".")

    def get_data_base(self) -> Any:
        return self.getSharedObject("db")

    def get_vtk_pipeline(self, id: str) -> VtkPipeline:
        return cast(VtkPipeline, self.get_data_base()[id])

    def get_grid_scale(self) -> vtkCubeAxesActor | None:
        return cast(vtkCubeAxesActor | None, self.getSharedObject("grid_scale"))

    def set_grid_scale(self, grid_scale: vtkCubeAxesActor) -> None:
        self.coreServer.setSharedObject("grid_scale", grid_scale)

    def get_axes(self) -> vtkAxesActor | None:
        return cast(vtkAxesActor | None, self.getSharedObject("axes"))

    def set_axes(self, axes: vtkAxesActor) -> None:
        self.coreServer.setSharedObject("axes", axes)

    def get_widget(self) -> vtkOrientationMarkerWidget | None:
        return cast(vtkOrientationMarkerWidget | None, self.getSharedObject("widget"))

    def set_widget(self, widget: vtkOrientationMarkerWidget) -> None:
        self.coreServer.setSharedObject("widget", widget)

    def get_viewer_data(self, data_id: str) -> ViewerData:
        if Data is None:
            raise Exception("Data model not available")

        with get_session() as session:
            if not session:
                raise Exception("No database session available")

            try:
                data = session.get(Data, data_id)
                if not data:
                    raise Exception(f"Data with id {data_id} not found in database")
                return ViewerData(
                    id=data.id,
                    viewable_file=data.viewable_file,
                    viewer_object=data.viewer_object,
                    viewer_elements_type=data.viewer_elements_type,
                )
            except Exception as e:
                print(f"Error fetching data {data_id}: {e}")
                raise

    def get_data_file_path(self, data_id: str, filename: str | None = None) -> str:
        if filename is None:
            data = self.get_viewer_data(data_id)
            viewable_file = data.viewable_file
            filename = str(viewable_file) if viewable_file is not None else ""

        data_folder_path = self.DATA_FOLDER_PATH
        if data_folder_path is None:
            raise Exception("DATA_FOLDER_PATH environment variable not set")

        return os.path.join(data_folder_path, data_id, filename)

    def get_renderer(self) -> vtkRenderer:
        return cast(vtkRenderer, self.getSharedObject("renderer"))

    def reset_camera_clipping_range(self) -> None:
        renderer = self.get_renderer()
        grid_scale = self.get_grid_scale()
        if grid_scale is not None and grid_scale.GetVisibility():
            grid_scale.SetUseBounds(True)
            renderer.ResetCameraClippingRange()
            grid_scale.SetUseBounds(False)
        else:
            renderer.ResetCameraClippingRange()

    def update_highlight(
        self,
        pipeline: VtkPipeline,
        id_to_select: int,
        field_type: str,
        dataset: vtkDataObject | None = None,
    ) -> None:
        node = pipeline.highlight.selectionNode
        node.SetContentType(vtkSelectionNode.INDICES)
        node.SetFieldType(
            vtkSelectionNode.CELL if field_type == "CELL" else vtkSelectionNode.POINT
        )
        selection_list = vtkIdTypeArray()
        selection_list.SetNumberOfComponents(1)
        selection_list.InsertNextValue(id_to_select)
        node.SetSelectionList(selection_list)
        target_dataset = dataset or pipeline.mapper.GetInputDataObject(0, 0)
        pipeline.highlight.extractSelection.SetInputData(0, target_dataset)
        pipeline.highlight.extractSelection.Modified()
        pipeline.highlight.extractSelection.Update()
        pipeline.highlight.actor.VisibilityOn()

    def clear_highlights(self, data_ids: list[str]) -> None:
        for data_id in data_ids:
            pipeline = self.get_vtk_pipeline(data_id)
            pipeline.highlight.actor.VisibilityOff()

    def _extract_blocks(
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
        return blocks

    def _prune_hidden_blocks(
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
                    self._prune_hidden_blocks(block, attributes)
                    if isinstance(block, vtkMultiBlockDataSet)
                    else block
                )
                pruned.SetBlock(index, child)
        return pruned

    def _get_block_style(self, pipeline: VtkPipeline, block_id: int) -> BlockStyle:
        if block_id not in pipeline.block_styles:
            style = BlockStyle(
                name="",
                attribute_location="point",
                points=[],
                minimum=0.0,
                maximum=1.0,
                item=0,
            )
            pipeline.block_styles[block_id] = style
        return pipeline.block_styles[block_id]

    def updateBlockColors(self, pipeline: VtkPipeline, block_id: int) -> None:
        block = pipeline.blockDataSets[block_id]
        if not isinstance(block, vtkDataSet):
            return

        style = self._get_block_style(pipeline, block_id)
        if not style["name"]:
            block.GetPointData().SetActiveScalars("")
            block.GetCellData().SetActiveScalars("")
            return

        field_data = (
            block.GetPointData()
            if style["attribute_location"] == "point"
            else block.GetCellData()
        )
        scalar_array = field_data.GetArray(style["name"])
        if not scalar_array:
            return

        lut = vtkColorTransferFunction()
        points = style["points"]
        minimum = style["minimum"]
        maximum = style["maximum"]
        if points:
            x_min, x_max = points[0], points[-4]
            span = x_max - x_min
            for i in range(0, len(points), 4):
                x, r, g, b = points[i : i + 4]
                new_x = (
                    minimum + (x - x_min) / span * (maximum - minimum)
                    if span
                    else minimum
                )
                lut.AddRGBPoint(new_x, r, g, b)
        else:
            lut.AddRGBPoint(minimum, 0, 0, 0)
            lut.AddRGBPoint(maximum, 1, 1, 1)

        lut.SetRange(minimum, maximum)
        rgba_colors = lut.MapScalars(scalar_array, 0, style.get("item", 0))
        rgba_colors.SetName(f"__colors_{style['name']}")

        field_data.AddArray(rgba_colors)
        field_data.SetActiveScalars(rgba_colors.GetName())

        other_field_data = (
            block.GetCellData()
            if style["attribute_location"] == "point"
            else block.GetPointData()
        )
        other_field_data.SetActiveScalars("")

        if isinstance(pipeline.mapper, vtkCompositePolyDataMapper):
            attributes = pipeline.mapper.GetCompositeDataDisplayAttributes()
            if attributes:
                attributes.RemoveBlockColor(block)
        pipeline.mapper.ScalarVisibilityOn()
        pipeline.mapper.SetColorModeToDirectScalars()
        pipeline.mapper.SetScalarModeToDefault()
        pipeline.mapper.Modified()

    def _sync_composite_pipeline(
        self, pipeline: VtkPipeline, dataset: vtkDataObject
    ) -> None:
        blocks = self._extract_blocks(dataset)
        mapper = cast(vtkCompositePolyDataMapper, pipeline.mapper)
        attributes = mapper.GetCompositeDataDisplayAttributes()
        print(f"[_sync_composite_pipeline] {attributes=}", flush=True)
        print(f"[_sync_composite_pipeline] {pipeline.block_styles=}", flush=True)
        color_rgb = [0.0, 0.0, 0.0]
        for source_block, destination_block in zip(pipeline.blockDataSets, blocks):
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
        pipeline.blockDataSets = blocks
        pipeline.mapper.SetInputDataObject(dataset)
        if pipeline.pick_mapper and isinstance(dataset, vtkMultiBlockDataSet):
            pipeline.pick_mapper.SetInputDataObject(
                self._prune_hidden_blocks(dataset, attributes)
            )
        for block_id in pipeline.block_styles:
            print(
                f"[_sync_composite_pipeline] Updating block colors for {block_id=}",
                flush=True,
            )
            self.updateBlockColors(pipeline, block_id)

    def _restore_active_scalars(
        self, source: vtkDataSet, target: vtkDataSet
    ) -> None:
        if active_points := source.GetPointData().GetScalars():
            target.GetPointData().SetActiveScalars(active_points.GetName())
        if active_cells := source.GetCellData().GetScalars():
            target.GetCellData().SetActiveScalars(active_cells.GetName())

    def set_clipping_planes(
        self, data_ids: list[str], planes_data: list[Plane]
    ) -> None:
        for data_id in data_ids:
            pipeline = self.get_vtk_pipeline(data_id)
            is_composite = isinstance(pipeline.mapper, vtkCompositePolyDataMapper)
            if not planes_data:
                if is_composite:
                    original_dataset = (
                        pipeline.filter.GetOutputDataObject(0)
                        if pipeline.filter
                        else pipeline.reader.GetOutputDataObject(0)
                    )
                    self._sync_composite_pipeline(pipeline, original_dataset)
                else:
                    pipeline.mapper.SetInputConnection(pipeline.reader.GetOutputPort())
                    reader_dataset = pipeline.reader.GetOutputAsDataSet()
                    self._restore_active_scalars(reader_dataset, reader_dataset)
                pipeline.clipping_filter = None
                continue
            clipping_filter = vtkExtractGeometry()
            geometry_filter = vtkGeometryFilter()
            if is_composite:
                clipping_filter.SetExecutive(vtkCompositeDataPipeline())
                geometry_filter.SetExecutive(vtkCompositeDataPipeline())
            clipping_filter.SetInputConnection(pipeline.reader.GetOutputPort())
            implicit_boolean = vtkImplicitBoolean()
            implicit_boolean.SetOperationTypeToIntersection()
            for plane_info in planes_data:
                plane = vtkPlane()
                plane.SetOrigin(plane_info.origin)
                plane.SetNormal(plane_info.normal)
                implicit_boolean.AddFunction(plane)
            clipping_filter.SetImplicitFunction(implicit_boolean)
            geometry_filter.SetInputConnection(clipping_filter.GetOutputPort())
            geometry_filter.Update()
            if is_composite:
                self._sync_composite_pipeline(
                    pipeline, geometry_filter.GetOutputDataObject(0)
                )
            else:
                pipeline.mapper.SetInputConnection(geometry_filter.GetOutputPort())
                reader_dataset = pipeline.reader.GetOutputAsDataSet()
                filtered_dataset = geometry_filter.GetOutputDataObject(0)
                self._restore_active_scalars(reader_dataset, filtered_dataset)
            pipeline.clipping_filter = clipping_filter

    def swap_pick_mappers(self, data_ids: list[str], use_pick_mapper: bool) -> None:
        # Swap actor mappers between the default and the pick_mapper (where hidden blocks are pruned).
        for data_id in data_ids:
            pipeline = self.get_vtk_pipeline(data_id)
            if pipeline.pick_mapper:
                mapper = pipeline.pick_mapper if use_pick_mapper else pipeline.mapper
                pipeline.actor.SetMapper(mapper)

    def pick_cell_or_point(
        self,
        data_ids: list[str],
        x: float,
        y: float,
        field_type: str,
        picker: vtkCellPicker,
    ) -> tuple[str | None, int]:
        self.swap_pick_mappers(data_ids, use_pick_mapper=True)
        try:
            picker.Pick(x, y, 0, self.get_renderer())
        finally:
            self.swap_pick_mappers(data_ids, use_pick_mapper=False)
        actor = picker.GetActor()
        # Find which pipeline owns the picked actor
        data_id = next(
            (
                current_data_id
                for current_data_id in data_ids
                if self.get_vtk_pipeline(current_data_id).actor == actor
            ),
            None,
        )
        id_to_select = (
            picker.GetCellId() if field_type == "CELL" else picker.GetPointId()
        )
        return data_id, id_to_select

    def pick_actors_under_coordinate(
        self, data_ids: list[str], x: float, y: float, picker: vtkCellPicker
    ) -> tuple[list[vtkActor], int]:
        renderer = self.get_renderer()
        self.swap_pick_mappers(data_ids, use_pick_mapper=True)
        actors = []
        viewer_id = -1
        try:
            picker.Pick(x, y, 0, renderer)
            viewer_id = picker.GetFlatBlockIndex()
            while actor := picker.GetActor():
                actors.append(actor)
                actor.SetPickable(False)
                picker.Pick(x, y, 0, renderer)
        finally:
            for actor in actors:
                actor.SetPickable(True)
            self.swap_pick_mappers(data_ids, use_pick_mapper=False)
        return actors, viewer_id

    def get_composite_block_info(
        self, pipeline: VtkPipeline, picker: vtkCellPicker
    ) -> tuple[vtkDataObject | None, str | None]:
        # Extract the specific block dataset and metadata from a picked composite flat index
        if not isinstance(pipeline.mapper, vtkCompositePolyDataMapper):
            return None, None
        flat_index = picker.GetFlatBlockIndex()
        if not (0 <= flat_index < len(pipeline.blockDataSets)):
            return None, None
        dataset = pipeline.blockDataSets[flat_index]
        geode_id = (
            pipeline.blockGeodeIds[flat_index]
            if flat_index < len(pipeline.blockGeodeIds)
            else None
        )
        return dataset, geode_id

    def get_array_values(self, array: Any, id_to_select: int) -> list[float] | float:
        components = array.GetNumberOfComponents()
        if components == 1:
            return float(array.GetComponent(id_to_select, 0))
        return [float(array.GetComponent(id_to_select, i)) for i in range(components)]

    def extract_picked_attributes(
        self,
        pipeline: VtkPipeline,
        id_to_select: int,
        field_type: str,
        dataset: vtkDataObject | None,
    ) -> dict[str, list[float] | float]:
        data_object = dataset or pipeline.reader.GetOutputDataObject(0)
        if not isinstance(data_object, vtkDataSet):
            return {}
        field_data = (
            data_object.GetCellData()
            if field_type == "CELL"
            else data_object.GetPointData()
        )
        attributes = {}
        for i in range(field_data.GetNumberOfArrays()):
            array = field_data.GetArray(i)
            if array and array.GetName():
                attributes[array.GetName()] = self.get_array_values(array, id_to_select)
        if field_type == "POINT" and (coords := data_object.GetPoint(id_to_select)):
            attributes["coordinates"] = list(coords)
        return attributes

    def update_grid_scale_and_clipping_range(self) -> None:
        grid_scale = self.get_grid_scale()
        if grid_scale is not None:
            renderer = self.get_renderer()
            if not grid_scale.GetVisibility():
                bounds = vtkBoundingBox()
                props = renderer.GetViewProps()
                props.InitTraversal()
                prop = props.GetNextProp()
                while prop:
                    if (
                        prop.GetVisibility()
                        and prop.GetUseBounds()
                        and prop != grid_scale
                    ):
                        prop_bounds = prop.GetBounds()
                        if prop_bounds is not None:
                            bounds.AddBounds(prop_bounds)
                    prop = props.GetNextProp()
                if bounds.IsValid():
                    final_bounds = [0.0] * 6
                    bounds.GetBounds(final_bounds)
                    grid_scale.SetBounds(final_bounds)

            final_bounds = list(grid_scale.GetBounds())
            if final_bounds[0] <= final_bounds[1]:

                def get_dist(axis: int) -> float:
                    p1 = [final_bounds[0], final_bounds[2], final_bounds[4]]
                    p2 = list(p1)
                    p2[axis] = final_bounds[axis * 2 + 1]
                    renderer.SetWorldPoint(p1[0], p1[1], p1[2], 1.0)
                    renderer.WorldToDisplay()
                    d1 = list(renderer.GetDisplayPoint())
                    renderer.SetWorldPoint(p2[0], p2[1], p2[2], 1.0)
                    renderer.WorldToDisplay()
                    d2 = list(renderer.GetDisplayPoint())
                    return math.sqrt((d1[0] - d2[0]) ** 2 + (d1[1] - d2[1]) ** 2)

                visibility_setters = [
                    grid_scale.SetXAxisLabelVisibility,
                    grid_scale.SetYAxisLabelVisibility,
                    grid_scale.SetZAxisLabelVisibility,
                ]

                for axis in range(3):
                    dist = get_dist(axis)
                    visibility_setter = visibility_setters[axis]

                    v1 = f"{final_bounds[axis * 2]:g}"
                    v2 = f"{final_bounds[axis * 2 + 1]:g}"
                    v_mid = (
                        f"{(final_bounds[axis * 2] + final_bounds[axis * 2 + 1]) / 2:g}"
                    )

                    char_width = 8
                    len1 = len(v1) * char_width
                    len2 = len(v2) * char_width
                    len_mid = len(v_mid) * char_width

                    hide_threshold = max(len1, len2) + 15
                    two_labels_threshold = (len1 + len2) * 1.1 + 30
                    three_labels_threshold = (len1 + len2 + len_mid) * 1.2 + 45

                    if dist < hide_threshold:
                        visibility_setter(False)
                    elif dist < two_labels_threshold:
                        visibility_setter(True)
                        labels = vtkStringArray()
                        labels.InsertNextValue(v1)
                        labels.InsertNextValue(v2)
                        grid_scale.SetAxisLabels(axis, labels)
                    elif dist < three_labels_threshold:
                        visibility_setter(True)
                        labels = vtkStringArray()
                        labels.InsertNextValue(v1)
                        labels.InsertNextValue(v_mid)
                        labels.InsertNextValue(v2)
                        grid_scale.SetAxisLabels(axis, labels)
                    else:
                        visibility_setter(True)
                        grid_scale.SetAxisLabels(axis, None)
        self.reset_camera_clipping_range()

    def update_scalar_bars_layout(self) -> None:
        visible_bars = []
        for data_id, pipeline in self.get_data_base().items():
            if (
                pipeline.scalarBar.GetVisibility()
                and pipeline.scalarBar.GetLookupTable() is not None
            ):
                visible_bars.append((data_id, pipeline.scalarBar))

        n = len(visible_bars)
        if n == 0:
            return

        start_x = 0.22
        start_y = 0.04
        margin_x = 0.03
        margin_y = 0.04

        cols = 5
        actual_width = 0.10
        row_height = 0.12

        for i, (data_id, bar) in enumerate(visible_bars):
            pipeline = self.get_vtk_pipeline(data_id)
            if pipeline.filter:
                dataset = pipeline.filter.GetOutputDataObject(0)
            else:
                dataset = pipeline.reader.GetOutputDataObject(0)

            attr_name = ""
            if dataset:
                pd = dataset.GetPointData().GetScalars()
                cd = dataset.GetCellData().GetScalars()
                if pd:
                    attr_name = pd.GetName()
                elif cd:
                    attr_name = cd.GetName()

            if not attr_name:
                attr_name = "Attribute"

            data_name = (
                dataset.GetObjectName()
                if dataset and dataset.GetObjectName()
                else data_id
            )

            bar.UnconstrainedFontSizeOn()
            bar.GetLabelTextProperty().SetFontSize(14)
            bar.GetTitleTextProperty().SetFontSize(14)
            bar.GetLabelTextProperty().SetColor(0, 0, 0)
            bar.GetTitleTextProperty().SetColor(0, 0, 0)
            bar.GetLabelTextProperty().SetShadow(False)
            bar.GetTitleTextProperty().SetShadow(False)

            if data_name:
                if len(data_name) > 22:
                    data_name = data_name[:19] + "..."
                bar.SetTitle(f"{attr_name}\n({data_name})\n")
                bar.GetTitleTextProperty().SetVerticalJustificationToTop()
                bar.GetTitleTextProperty().SetLineOffset(0.0)
                bar.SetBarRatio(0.15)
                bar_height = 0.12
            else:
                bar.SetTitle(f"{attr_name}\n")
                bar.GetTitleTextProperty().SetVerticalJustificationToTop()
                bar.GetTitleTextProperty().SetLineOffset(0.0)
                bar.SetBarRatio(0.4)
                bar_height = 0.08

            bar.SetNumberOfLabels(2)
            bar.SetLabelFormat("%.2g")
            bar.SetOrientationToHorizontal()

            row = i // cols
            col = i % cols

            x = start_x + col * (actual_width + margin_x)
            y = start_y + row * (row_height + margin_y)

            bar.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
            bar.GetPositionCoordinate().SetValue(x, y)
            bar.SetWidth(actual_width)
            bar.SetHeight(bar_height)

    def render(self, view: int = -1) -> None:
        self.update_grid_scale_and_clipping_range()
        self.getSharedObject("publisher").imagePush({"view": view})

    def register_object(self, id: str, data: VtkPipeline) -> None:
        self.get_data_base()[id] = data

    def deregister_object(self, id: str) -> None:
        if id in self.get_data_base():
            del self.get_data_base()[id]
