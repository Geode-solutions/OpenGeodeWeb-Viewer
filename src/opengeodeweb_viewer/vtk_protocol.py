# Standard library imports
import math
import os
from typing import cast, Any, Literal
from dataclasses import dataclass, field

# Third party imports
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.web import protocols as vtk_protocols
from vtkmodules.vtkIOXML import (
    vtkXMLReader,
)
from vtkmodules.vtkWebCore import vtkWebApplication
from vtkmodules.vtkCommonExecutionModel import vtkAlgorithm
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkDataSetMapper,
)
from vtkmodules.vtkCommonDataModel import (
    vtkDataObject,
    vtkDataSet,
    vtkBoundingBox,
    vtkSelection,
    vtkSelectionNode,
)
from vtkmodules.vtkFiltersExtraction import vtkExtractSelection
from vtkmodules.vtkCommonCore import vtkStringArray, vtkIdTypeArray
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor, vtkAxesActor, vtkScalarBarActor
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget

# Local application imports
from opengeodeweb_microservice.database.connection import get_session
from opengeodeweb_microservice.database.data import Data
from opengeodeweb_microservice.database.data_types import ViewerType, ViewerElementsType


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
class VtkPipeline:
    reader: vtkXMLReader
    mapper: vtkMapper
    filter: vtkAlgorithm | None = None
    actor: vtkActor = field(default_factory=vtkActor)
    highlight: HighlightPipeline = field(default_factory=HighlightPipeline)
    blockDataSets: list[vtkDataObject | None] = field(default_factory=list)
    blockGeodeIds: list[str] = field(default_factory=list)
    scalarBar: vtkScalarBarActor = field(default_factory=vtkScalarBarActor)


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
        if dataset is not None:
            pipeline.highlight.extractSelection.SetInputData(0, dataset)
        pipeline.highlight.extractSelection.Modified()
        pipeline.highlight.extractSelection.Update()
        pipeline.highlight.actor.VisibilityOn()

    def clear_highlights(self, ids: list[str]) -> None:
        for data_id in ids:
            pipeline = self.get_vtk_pipeline(data_id)
            pipeline.highlight.actor.VisibilityOff()

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
            if pipeline.scalarBar.GetVisibility() and pipeline.scalarBar.GetLookupTable() is not None:
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
            dataset = pipeline.reader.GetOutputAsDataSet()
            
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
                
            data_name = ""
            try:
                name_file_path = self.get_data_file_path(data_id, "name.txt")
                if os.path.exists(name_file_path):
                    with open(name_file_path, "r") as f:
                        data_name = f.read().strip()
            except Exception:
                pass
                
            bar.UnconstrainedFontSizeOn()
            bar.GetLabelTextProperty().SetFontSize(14)
            bar.GetTitleTextProperty().SetFontSize(14)
            bar.GetLabelTextProperty().SetColor(0, 0, 0)
            bar.GetTitleTextProperty().SetColor(0, 0, 0)
            bar.GetLabelTextProperty().SetShadow(False)
            bar.GetTitleTextProperty().SetShadow(False)
            
            if data_name:
                if len(data_name) > 30:
                    data_name = data_name[:27] + "..."
                bar.SetTitle(f"{attr_name}\n({data_name})")
                bar.GetTitleTextProperty().SetVerticalJustificationToTop()
                bar.GetTitleTextProperty().SetLineOffset(0.0)
                bar.SetBarRatio(0.15)
                bar_height = 0.12
            else:
                bar.SetTitle(attr_name)
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
