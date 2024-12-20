# Standard library imports
import os

# Third party imports
import vtk
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.object.object_methods import VtkObjectView

class VtkModelView(VtkObjectView):
    model_prefix = "opengeodeweb_viewer.model."
    model_schemas_dict = get_schemas_dict(os.path.join(os.path.dirname(__file__), "schemas"))

    def __init__(self):
        super().__init__()
    
    @exportRpc(model_prefix + model_schemas_dict["register"]["rpc"])
    def registerModel(self, params):
        print(self.model_prefix + self.model_schemas_dict["register"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.model_schemas_dict["register"])
        id = params["id"]
        file_name = params["file_name"]
        try:
            reader = vtk.vtkXMLMultiBlockDataReader()
            filter = vtk.vtkGeometryFilter()
            filter.SetInputConnection(reader.GetOutputPort())
            mapper = vtk.vtkCompositePolyDataMapper()
            mapper.SetInputConnection(filter.GetOutputPort())
            self.registerObject(id, file_name, reader, filter, mapper)
        except Exception as e:
            print("error : ", str(e), flush=True)

    @exportRpc(model_prefix + model_schemas_dict["deregister"]["rpc"])
    def deregisterModel(self, params):
        print(self.model_prefix + self.model_schemas_dict["deregister"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.model_schemas_dict["deregister"])
        id = params["id"]
        self.deregisterObject(id)

    @exportRpc(model_prefix + model_schemas_dict["set_mesh_visibility"]["rpc"])
    def setMeshVisibility(self, params):
        print(self.model_prefix + self.model_schemas_dict["set_mesh_visibility"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.model_schemas_dict["set_mesh_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        self.SetEdgesVisibility(id, visibility)

    @exportRpc(model_prefix + model_schemas_dict["set_components_visibility"]["rpc"])
    def setComponentsVisibility(self, params):
        print(self.model_prefix + self.model_schemas_dict["set_components_visibility"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.model_schemas_dict["set_components_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        self.SetVisibility(id, visibility)

    @exportRpc(model_prefix + model_schemas_dict["set_components_color"]["rpc"])
    def setComponentsColor(self, params):
        print(self.model_prefix + self.model_schemas_dict["set_components_color"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.model_schemas_dict["set_components_color"])
        id = params["id"]
        red, green, blue = params["color"]["r"], params["color"]["g"], params["color"]["b"]
        self.SetColor(id, red, green, blue)

