# Standard library imports
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
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor, vtkAxesActor
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget

# Local application imports
from opengeodeweb_microservice.database.connection import get_session
from opengeodeweb_microservice.database.data import Data


@dataclass
class vtkData:
    reader: vtkXMLReader
    mapper: vtkMapper
    filter: vtkAlgorithm | None = None
    actor: vtkActor = field(default_factory=vtkActor)
    max_dimension: Literal["points", "edges", "polygons", "polyhedra", "default"] = (
        "default"
    )


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

    def get_object(self, id: str) -> vtkData:
        return cast(vtkData, self.get_data_base()[id])

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

    def get_viewer_object_type(self, data_id: str) -> str:
        data = self.get_data(data_id)
        object_type = data.get("object_type")
        if object_type == "mesh":
            return "mesh"
        elif object_type == "model":
            return "model"
        raise Exception(f"Unknown object_type type: {object_type}")

    def get_data(self, data_id: str) -> dict[str, str | list[str] | None]:
        if Data is None:
            raise Exception("Data model not available")

        with get_session() as session:
            if not session:
                raise Exception("No database session available")

            try:
                data = session.get(Data, data_id)
                if not data:
                    raise Exception(f"Data with id {data_id} not found in database")

                return {
                    "id": data.id,
                    "viewable_file": data.viewable_file,
                    "viewer_object": data.viewer_object,
                }
            except Exception as e:
                print(f"Error fetching data {data_id}: {e}")
                raise

    def get_data_file_path(self, data_id: str, filename: str | None = None) -> str:
        if filename is None:
            data = self.get_data(data_id)
            viewable_file = data["viewable_file"]
            filename = str(viewable_file) if viewable_file is not None else ""

        data_folder_path = self.DATA_FOLDER_PATH
        if data_folder_path is None:
            raise Exception("DATA_FOLDER_PATH environment variable not set")

        return os.path.join(data_folder_path, data_id, filename)

    def get_renderer(self) -> vtkRenderer:
        return cast(vtkRenderer, self.getSharedObject("renderer"))

    def render(self, view: int = -1) -> None:
        grid_scale = self.get_grid_scale()
        if grid_scale is not None:
            renderer = self.get_renderer()
            renderer_bounds = renderer.ComputeVisiblePropBounds()
            grid_scale.SetBounds(renderer_bounds)
        self.getSharedObject("publisher").imagePush({"view": view})

    def register_object(self, id: str, data: vtkData) -> None:
        self.get_data_base()[id] = data

    def deregister_object(self, id: str) -> None:
        if id in self.get_data_base():
            del self.get_data_base()[id]
