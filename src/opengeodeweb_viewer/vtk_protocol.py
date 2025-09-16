# Standard library imports
import os
import sqlite3

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols

# Local application imports


class VtkView(vtk_protocols.vtkWebProtocol):
    def __init__(self):
        super().__init__()
        self.DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH")
        # self.DATABASE_PATH = os.getenv("DATABASE_PATH")
        self.DataReader = vtk.vtkXMLPolyDataReader()
        self.ImageReader = vtk.vtkXMLImageDataReader()

    def get_data_base(self):
        return self.getSharedObject("db")

    def get_db_connection(self):
        conn = sqlite3.connect(self.DATA_FOLDER_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def get_data_by_id(self, data_id):
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data WHERE id = ?", (data_id,))
            data = cursor.fetchone()
            return dict(data) if data else None
        finally:
            conn.close()

    def get_all_data(self):
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data")
            data = cursor.fetchall()
            return [dict(row) for row in data]
        finally:
            conn.close()

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
