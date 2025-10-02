# Standard library imports
import os

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols

# Local application imports
from opengeodeweb_microservice.database.connection import get_session
from opengeodeweb_microservice.database.data import Data


class VtkView(vtk_protocols.vtkWebProtocol):
    def __init__(self) -> None:
        super().__init__()
        self.DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH")
        self.DATABASE_PATH = os.getenv("DATABASE_PATH")
        self.DataReader = vtk.vtkXMLPolyDataReader()
        self.ImageReader = vtk.vtkXMLImageDataReader()

    def get_data_base(self) -> dict[str, dict[str, object | str]]:
        return self.getSharedObject("db")

    def get_object(self, id: str) -> dict[str, object | str]:
        return self.get_data_base()[id]

    def get_data(self, data_id: str) -> dict[str, str | list[str] | None]:
        if Data is None:
            raise Exception("Data model not available")

        session = get_session()
        if not session:
            raise Exception("No database session available")

        try:
            data = session.get(Data, data_id)
            if not data:
                raise Exception(f"Data with id {data_id} not found in database")

            return {
                "id": data.id,
                "native_file_name": data.native_file_name,
                "viewable_file_name": data.viewable_file_name,
                "geode_object": data.geode_object,
                "light_viewable": data.light_viewable,
                "input_file": data.input_file,
                "additional_files": data.additional_files,
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
