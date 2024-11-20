# Standard library imports
import json
import os

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.object.protocols import VtkObjectView

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
schemas_dict = get_schemas_dict(schemas_dir)

class VtkModelView(VtkObjectView):
    def __init__(self):
        super().__init__()

    @exportRpc(schemas_dict["set_model_mesh_visibility"]["rpc"])
    def SetModelMeshVisibility(self, params):
        validate_schema(params, schemas_dict["set_model_mesh_visibility"])
        super().SetEdgeVisibility(params)

    @exportRpc(schemas_dict["set_model_components_visibility"]["rpc"])
    def SetModelComponentsVisibility(self, params):
        validate_schema(params, schemas_dict["set_model_components_visibility"])
        super().SetVisibility(params)

    @exportRpc(schemas_dict["set_model_components_color"]["rpc"])
    def SetModelComponentsColor(self, id, object_type, color):
        validate_schema(params, schemas_dict["set_model_components_color"])
        super().SetColor(params)

    @exportRpc(schemas_dict["set_model_corners_size"]["rpc"])
    def setModelCornersSize(self, params):
        validate_schema(params, schemas_dict["set_model_corners_size"])
        super().SetPointSize(params)