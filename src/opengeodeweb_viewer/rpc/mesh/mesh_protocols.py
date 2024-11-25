# Standard library imports
import json
import os

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols
from vtkmodules.vtkIOImage import vtkPNGWriter, vtkJPEGWriter
from vtkmodules.vtkRenderingCore import (vtkWindowToImageFilter)
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.object.object_methods import VtkObjectView

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
schemas_dict = get_schemas_dict(schemas_dir)
prefix = "opengeodeweb_viewer.mesh."

class VtkMeshView(VtkObjectView):
    def __init__(self):
        super().__init__()
        self.prefix = prefix
        self.schemas_dict = schemas_dict

    @exportRpc(prefix + schemas_dict["register"]["rpc"])
    def registerMesh(self, params):
        print(schemas_dict["register"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["register"])
        id = params["id"]
        file_name = params["file_name"]
        try:
            reader = vtk.vtkXMLGenericDataObjectReader()
            filter = {}
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            self.register(id, file_name, reader, filter, mapper)
        except Exception as e:
            print("error : ", str(e), flush=True)

    @exportRpc(prefix + schemas_dict["deregister"]["rpc"])
    def deregisterMesh(self, params):
        print(schemas_dict["deregister"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["deregister"])
        id = params["id"]
        self.deregister(id)

    @exportRpc(prefix + schemas_dict["set_visibility"]["rpc"])
    def SetMeshVisibility(self, params):
        print(schemas_dict["set_visibility"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["set_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        self.SetVisibility(id, visibility)

    @exportRpc(prefix + schemas_dict["set_opacity"]["rpc"])
    def SetMeshOpacity(self, params):
        print(schemas_dict["set_opacity"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["set_opacity"])
        id = params["id"]
        opacity = float(params["opacity"])
        self.SetOpacity(id, opacity)

    @exportRpc(prefix + schemas_dict["set_edge_visibility"]["rpc"])
    def setMeshEdgeVisibility(self, params):
        print(schemas_dict["set_edge_visibility"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["set_edge_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        self.SetEdgeVisibility(id, visibility)

    @exportRpc(prefix + schemas_dict["set_point_visibility"]["rpc"])
    def setMeshPointVisibility(self, params):
        print(schemas_dict["set_point_visibility"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["set_point_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        self.SetVertexVisibility(id, visibility)

    @exportRpc(prefix + schemas_dict["set_point_size"]["rpc"])
    def setMeshPointSize(self, params):
        print(schemas_dict["set_point_size"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["set_point_size"])
        id = params["id"]
        size = float(params["size"])
        self.SetPointSize(id, size)

    @exportRpc(prefix + schemas_dict["set_color"]["rpc"])
    def setMeshColor(self, params):
        print(schemas_dict["set_color"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["set_color"])
        id = params["id"]
        red = params["red"]
        green = params["green"]
        blue = params["blue"]
        self.SetColor(id, red, green, blue)

    @exportRpc(prefix + schemas_dict["display_vertex_attribute"]["rpc"])
    def setVertexAttribute(self, params):
        print(schemas_dict["display_vertex_attribute"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["display_vertex_attribute"])
        id = params["id"]
        name = params["name"]
        reader = self.get_object(id)["reader"]
        points = reader.GetOutput().GetPointData()
        points.SetActiveScalars(name)
        mapper = self.get_object(id)["mapper"]
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointData()
        mapper.SetScalarRange(points.GetScalars().GetRange())
        self.render()

    @exportRpc(prefix + schemas_dict["display_polygon_attribute"]["rpc"])
    def setPolygonAttribute(self, params):
        print(schemas_dict["display_polygon_attribute"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["display_polygon_attribute"])
        id = params["id"]
        name = params["name"]
        reader = self.get_object(id)["reader"]
        cells = reader.GetOutput().GetCellData()
        cells.SetActiveScalars(name)
        mapper = self.get_object(id)["mapper"]
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUseCellData()
        mapper.SetScalarRange(cells.GetScalars().GetRange())
        self.render()