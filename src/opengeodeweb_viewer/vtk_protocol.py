# Standard library imports
import os

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols  # type: ignore

# Local application imports
from opengeodeweb_microservice.database.connection import get_session
from opengeodeweb_microservice.database.data import Data

# mypy: allow-untyped-defs


class VtkView(vtk_protocols.vtkWebProtocol):
    def __init__(self) -> None:
        super().__init__()
        self.DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH")
        self.DataReader = vtk.vtkXMLPolyDataReader()
        self.ImageReader = vtk.vtkXMLImageDataReader()

    def get_data_base(self) -> dict[str, dict[str, object | str]]:
        return self.getSharedObject("db")

    def get_object(self, id: str) -> dict[str, object | str]:
        return self.get_data_base()[id]

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
                    "viewable_file_name": data.viewable_file_name,
                    "viewer_object": data.viewer_object,
                }
            except Exception as e:
                print(f"Error fetching data {data_id}: {e}")
                raise

    def get_data_file_path(self, data_id: str, filename: str | None = None) -> str:
        if filename is None:
            data = self.get_data(data_id)
            viewable_file_name = data["viewable_file_name"]
            filename = str(viewable_file_name) if viewable_file_name is not None else ""

        data_folder_path = self.DATA_FOLDER_PATH
        if data_folder_path is None:
            raise Exception("DATA_FOLDER_PATH environment variable not set")

        return os.path.join(data_folder_path, data_id, filename)

    def get_renderer(self) -> vtk.vtkRenderer:
        return self.getSharedObject("renderer")

    def get_protocol(self, name: str) -> vtk_protocols.vtkWebProtocol:
        for p in self.coreServer.getLinkProtocols():
            if type(p).__name__ == name:
                return p

    def render(self, view: int = -1) -> None:
        if "grid_scale" in self.get_data_base():
            renderer = self.get_renderer()
            renderer_bounds = renderer.ComputeVisiblePropBounds()
            grid_scale = self.get_object("grid_scale")["actor"]
            grid_scale.SetBounds(renderer_bounds)
        self.getSharedObject("publisher").imagePush({"view": view})

    def register_object(
        self,
        id: str,
        reader: vtk.vtkAlgorithm,
        filter: vtk.vtkAlgorithm,
        actor: vtk.vtkActor,
        mapper: vtk.vtkMapper,
        textures: dict[str, str | int | float],
    ) -> None:
        self.get_data_base()[id] = {
            "reader": reader,
            "filter": filter,
            "actor": actor,
            "mapper": mapper,
            "textures": textures,
        }

    def deregister_object(self, id: str) -> None:
        if id in self.get_data_base():
            del self.get_data_base()[id]
