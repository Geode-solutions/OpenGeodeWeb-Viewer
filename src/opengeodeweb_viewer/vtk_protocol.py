# Standard library imports
import os

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols

# Local application imports
from opengeodeweb_microservice.database.connection import init_database, get_session
from opengeodeweb_microservice.database.data import Data


class VtkView(vtk_protocols.vtkWebProtocol):
    def __init__(self):
        super().__init__()
        self.DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH")
        self.DATABASE_PATH = os.getenv("DATABASE_PATH")
        self.DataReader = vtk.vtkXMLPolyDataReader()
        self.ImageReader = vtk.vtkXMLImageDataReader()

        if self.DATABASE_PATH:
            db_full_path = os.path.join(self.DATABASE_PATH, "project.db")
            init_database(db_full_path)

    def get_data_base(self):
        return self.getSharedObject("db")

    def get_data(self, data_id):
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

    def get_data_file_path(self, data_id, filename=None):
        if filename is None:
            data = self.get_data(data_id)
            filename = data["viewable_file_name"]

        return os.path.join(self.DATA_FOLDER_PATH, data_id, filename)

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
        if id in self.get_data_base():
            del self.get_data_base()[id]
