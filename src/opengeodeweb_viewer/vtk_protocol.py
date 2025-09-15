# Standard library imports
import os

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols

# Local application imports
from opengeodeweb_microservice.database.data import Data
from opengeodeweb_microservice.database.connection import get_session


class VtkView(vtk_protocols.vtkWebProtocol):
    def __init__(self):
        super().__init__()
        self.DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH")
        self.DataReader = vtk.vtkXMLPolyDataReader()
        self.ImageReader = vtk.vtkXMLImageDataReader()

    def get_data_info(self, id: str) -> Data:
        data_entry = Data.get(id)
        if not data_entry:
            raise ValueError(f"Data with id {id} not found")
        return data_entry

    def get_data_file_path(self, id: str, filename: str = "") -> str:
        data_entry = self.get_data_info(id)
        if filename:
            return os.path.join(self.DATA_FOLDER_PATH, id, filename)
        return os.path.join(self.DATA_FOLDER_PATH, id, data_entry.native_file_name)

    def load_data(self, id: str):
        data_entry = self.get_data_info(id)
        file_path = self.get_data_file_path(id, data_entry.native_file_name)

        # if not os.path.exists(file_path):
        #     raise FileNotFoundError(f"File not found at {file_path}")

        if file_path.endswith(".vtp"):
            reader = vtk.vtkXMLPolyDataReader()
        elif file_path.endswith(".vti"):
            reader = vtk.vtkXMLImageDataReader()
        elif file_path.endswith(".vtu"):
            reader = vtk.vtkXMLUnstructuredGridReader()
        else:
            raise ValueError(f"Unsupported file extension for {file_path}")

        reader.SetFileName(file_path)
        return reader, data_entry.geode_object

    def get_data_base(self):
        return self.getSharedObject("db")

    def get_renderer(self):
        return self.getSharedObject("renderer")

    def get_object(self, id):
        return self.get_data_base()[id]

    def get_protocol(self, name):
        for p in self.coreServer.getLinkProtocols():
            if type(p).__name__ == name:
                return p

    def render(self, view=-1):
        if "grid_scale" in self.get_data_base():
            renderer = self.get_renderer()
            renderer_bounds = renderer.ComputeVisiblePropBounds()
            grid_scale = self.get_object("grid_scale")["actor"]
            grid_scale.SetBounds(renderer_bounds)
        self.getSharedObject("publisher").imagePush({"view": view})

    def register_object(self, id, reader, filter, actor, mapper, textures):
        self.get_data_base()[id] = {
            "reader": reader,
            "filter": filter,
            "actor": actor,
            "mapper": mapper,
            "textures": textures,
        }

    def deregister_object(self, id):
        del self.get_data_base()[id]
