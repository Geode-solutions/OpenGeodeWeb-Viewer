# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView

class VtkMeshEdgesView(VtkMeshView):
    mesh_edges_prefix = "opengeodeweb_viewer.mesh.edges."
    mesh_edges_schemas_dict = get_schemas_dict(os.path.join(os.path.dirname(__file__), "schemas"))

    def __init__(self):
        super().__init__()

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["visibility"]["rpc"])
    def setMeshEdgesVisibility(self, params):
        print(self.mesh_edges_prefix + self.mesh_edges_schemas_dict["visibility"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_edges_schemas_dict["visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        self.SetEdgesVisibility(id, visibility)

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["color"]["rpc"])
    def setMeshEdgesColor(self, params):
        print(self.mesh_edges_prefix + self.mesh_edges_schemas_dict["color"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_edges_schemas_dict["color"])
        id = params["id"]
        red, green, blue = params["color"]["r"]/255, params["color"]["g"]/255, params["color"]["b"]/255
        self.SetEdgesColor(id, [red, green, blue])

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["size"]["rpc"])
    def setMeshEdgesSize(self, params):
        print(self.mesh_edges_prefix + self.mesh_edges_schemas_dict["size"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_edges_schemas_dict["size"])
        id = params["id"]
        size = bool(params["size"])
        self.SetEdgesSize(id, size)


    
