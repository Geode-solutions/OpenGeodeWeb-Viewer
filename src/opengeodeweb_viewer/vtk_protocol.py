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
    vtkCompositePolyDataMapper,
)
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkBoundingBox
from vtkmodules.vtkCommonCore import vtkStringArray
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor, vtkAxesActor
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
class VtkPipeline:
    reader: vtkXMLReader
    highlightMapper: vtkMapper
    mapper: vtkMapper
    filter: vtkAlgorithm | None = None
    actor: vtkActor = field(default_factory=vtkActor)
    highlightActor: vtkActor = field(default_factory=vtkActor)
    blockDataSets: list[vtkDataObject | None] = field(default_factory=list)
    blockGeodeIds: list[str] = field(default_factory=list)
    activeHighlightIds: list[int] = field(default_factory=list)


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

    def update_grid_scale_and_clipping_range(self) -> None:
        grid_scale = self.get_grid_scale()
        if grid_scale is not None:
            renderer = self.get_renderer()
            bounds = vtkBoundingBox()
            props = renderer.GetViewProps()
            props.InitTraversal()
            prop = props.GetNextProp()
            while prop:
                if prop.GetUseBounds() and prop != grid_scale:
                    bounds.AddBounds(prop.GetBounds())
                prop = props.GetNextProp()
            if bounds.IsValid():
                final_bounds = [0.0] * 6
                bounds.GetBounds(final_bounds)
                grid_scale.SetBounds(final_bounds)

                def get_dist(axis):
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
                    v_mid = f"{(final_bounds[axis * 2] + final_bounds[axis * 2 + 1]) / 2:g}"

                    len1 = len(v1) * 10
                    len2 = len(v2) * 10
                    len_mid = len(v_mid) * 10

                    if dist < max(len1, len2) + 40:
                        visibility_setter(False)
                    elif dist < (len1 + len2) * 2.0 + 80:
                        visibility_setter(True)
                        labels = vtkStringArray()
                        labels.InsertNextValue(v1)
                        labels.InsertNextValue(v2)
                        grid_scale.SetAxisLabels(axis, labels)
                    elif dist < (len1 + len2 + len_mid) * 2.2 + 120:
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

    def render(self, view: int = -1) -> None:
        self.update_grid_scale_and_clipping_range()
        self.getSharedObject("publisher").imagePush({"view": view})

    def register_object(self, id: str, data: VtkPipeline) -> None:
        self.get_data_base()[id] = data

    def deregister_object(self, id: str) -> None:
        if id in self.get_data_base():
            del self.get_data_base()[id]
