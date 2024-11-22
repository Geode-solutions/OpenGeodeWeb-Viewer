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
from opengeodeweb_viewer.object.methods import VtkObjectView


schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
schemas_dict = get_schemas_dict(schemas_dir)

class VtkMeshView(VtkObjectView):
    def __init__(self):
        super().__init__()

    @exportRpc(schemas_dict["register"]["rpc"])
    def register(self, params):
        validate_schema(params, schemas_dict["register"])
        id = params["id"]
        file_name = params["file_name"]
        try:
            reader = vtk.vtkXMLGenericDataObjectReader()
            filter = {}
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            super().register(id, file_name, reader, filter, mapper)
        except Exception as e:
            print("error : ", str(e), flush=True)

    @exportRpc(schemas_dict["deregister"]["rpc"])
    def deregisterMesh(self, params):
        validate_schema(params, schemas_dict["deregister"])
        id = params["id"]
        super().deregister(id)

    @exportRpc(schemas_dict["set_visibility"]["rpc"])
    def SetVisibility(self, params):
        print(schemas_dict["set_visibility"]["rpc"], flush=True)
        validate_schema(params, schemas_dict["set_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        super().SetVisibility(id, visibility)

    @exportRpc(schemas_dict["set_opacity"]["rpc"])
    def SetOpacity(self, params):
        print(schemas_dict["set_opacity"]["rpc"], flush=True)
        validate_schema(params, schemas_dict["set_opacity"])
        id = params["id"]
        opacity = float(params["opacity"])
        super().SetOpacity(id, opacity)

    @exportRpc(schemas_dict["set_edge_visibility"]["rpc"])
    def setEdgeVisibility(self, params):
        print(schemas_dict["set_edge_visibility"]["rpc"], flush=True)
        validate_schema(params, schemas_dict["set_edge_visibility"])
        print(f"{params=}", flush=True)
        id = params["id"]
        visibility = bool(params["visibility"])
        super().SetEdgeVisibility(id, visibility)

    @exportRpc(schemas_dict["set_point_visibility"]["rpc"])
    def setPointVisibility(self, params):
        print(schemas_dict["set_point_visibility"]["rpc"], flush=True)
        validate_schema(params, schemas_dict["set_point_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        super().SetVertexVisibility(id, visibility)

    @exportRpc(schemas_dict["set_point_size"]["rpc"])
    def setPointSize(self, params):
        print(schemas_dict["set_point_size"]["rpc"], flush=True)
        validate_schema(params, schemas_dict["set_point_size"])
        id = params["id"]
        size = float(params["size"])
        super().SetPointSize(id, size)

    @exportRpc(schemas_dict["set_color"]["rpc"])
    def setColor(self, params):
        print(schemas_dict["set_color"]["rpc"], flush=True)
        validate_schema(params, schemas_dict["set_color"])
        id = params["id"]
        red = params["red"]
        green = params["green"]
        blue = params["blue"]
        super().SetColor(id, red, green, blue)

    @exportRpc(schemas_dict["display_vertex_attribute"]["rpc"])
    def setVertexAttribute(self, params):
        validate_schema(params, schemas_dict["display_vertex_attribute"])
        print(f"{params=}", flush=True)
        id = params["id"]
        name = params["name"]
        mapper = super().get_object(id)["mapper"]
        mapper.SelectColorArray(name)
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointFieldData()
        super().render()

    @exportRpc(schemas_dict["display_polygon_attribute"]["rpc"])
    def setPolygonAttribute(self, params):
        validate_schema(params, schemas_dict["display_polygon_attribute"])
        id = params["id"]
        name = params["name"]
        print(f"{id=}", flush=True)
        print(f"{name=}", flush=True)
        mapper = super().get_object(id)["mapper"]
        mapper.SelectColorArray(name)
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUseCellFieldData()
        super().render()