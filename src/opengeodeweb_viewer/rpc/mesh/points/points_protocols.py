# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView

class VtkMeshPointsView(VtkMeshView):
    prefix = "opengeodeweb_viewer.mesh.points."
    schemas_dict = get_schemas_dict(os.path.join(os.path.dirname(__file__), "schemas"))

    def __init__(self):
        super().__init__()

    @exportRpc(prefix + schemas_dict["visibility"]["rpc"])
    def setMeshPointsVisibility(self, params):
        print(self.schemas_dict["visibility"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.schemas_dict["visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        self.SetVertexVisibility(id, visibility)

    @exportRpc(prefix + schemas_dict["color"]["rpc"])
    def setMeshPointsSize(self, params):
        print(self.schemas_dict["color"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.schemas_dict["color"])
        id = params["id"]
        color = params["color"]
        self.SetPointsColor(id, color)

    @exportRpc(prefix + schemas_dict["size"]["rpc"])
    def setMeshPointsSize(self, params):
        print(self.schemas_dict["size"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.schemas_dict["size"])
        id = params["id"]
        size = float(params["size"])
        self.SetPointSize(id, size)

    @exportRpc(prefix + schemas_dict["vertex_attribute"]["rpc"])
    def setMeshPointsVertexAttribute(self, params):
        print(self.schemas_dict["vertex_attribute"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.schemas_dict["vertex_attribute"])
        id = params["id"]
        name = str(params["name"])
        self.setMeshVertexAttribute(id, name)
    