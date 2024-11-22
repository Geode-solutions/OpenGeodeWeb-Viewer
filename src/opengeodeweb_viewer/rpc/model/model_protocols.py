# Standard library imports
import json
import os

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.object.object_methods import VtkObjectView

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
schemas_dict = get_schemas_dict(schemas_dir)

class VtkModelView(VtkObjectView):
    def __init__(self):
        super().__init__()
    
    @exportRpc(schemas_dict["register"]["rpc"])
    def registerModel(self, params):
        print(schemas_dict["register"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["register"])
        id = params["id"]
        file_name = params["file_name"]
        try:
            reader = vtk.vtkXMLMultiBlockDataReader()
            filter = vtk.vtkGeometryFilter()
            filter.SetInputConnection(reader.GetOutputPort())
            mapper = vtk.vtkCompositePolyDataMapper()
            mapper.SetInputConnection(filter.GetOutputPort())
            super().register(id, file_name, reader, filter, mapper)
        except Exception as e:
            print("error : ", str(e), flush=True)

    @exportRpc(schemas_dict["deregister"]["rpc"])
    def deregisterModel(self, params):
        print(schemas_dict["deregister"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["deregister"])
        id = params["id"]
        super().deregister(id)

    @exportRpc(schemas_dict["set_mesh_visibility"]["rpc"])
    def SetMeshVisibility(self, params):
        print(schemas_dict["set_mesh_visibility"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["set_mesh_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        super().SetEdgeVisibility(id, visibility)

    @exportRpc(schemas_dict["set_components_visibility"]["rpc"])
    def SetComponentsVisibility(self, params):
        print(schemas_dict["set_components_visibility"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["set_components_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        super().SetVisibility(id, visibility)

    @exportRpc(schemas_dict["set_components_color"]["rpc"])
    def SetComponentsColor(self, params):
        print(schemas_dict["set_components_color"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["set_components_color"])
        id = params["id"]
        red = params["red"]
        green = params["green"]
        blue = params["blue"]
        super().SetColor(id, red, green, blue)

    @exportRpc(schemas_dict["set_corners_size"]["rpc"])
    def setCornersSize(self, params):
        print(schemas_dict["set_corners_size"]["rpc"], params, flush=True)
        validate_schema(params, schemas_dict["set_corners_size"])
        id = params["id"]
        size = float(params["size"])
        super().SetPointSize(id, size)