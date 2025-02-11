# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView

class VtkMeshPointsView(VtkMeshView):
    mesh_points_prefix = "opengeodeweb_viewer.mesh.points."
    mesh_points_schemas_dict = get_schemas_dict(os.path.join(os.path.dirname(__file__), "schemas"))

    def __init__(self):
        super().__init__()

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["visibility"]["rpc"])
    def setMeshPointsVisibility(self, params):
        print(self.mesh_points_prefix + self.mesh_points_schemas_dict["visibility"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_points_schemas_dict["visibility"])
        id = str(params["id"])
        visibility = bool(params["visibility"])
        self.SetPointsVisibility(id, visibility)

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["color"]["rpc"])
    def setMeshPointsColor(self, params):
        print(self.mesh_points_prefix + self.mesh_points_schemas_dict["color"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_points_schemas_dict["color"])
        id = str(params["id"])
        red, green, blue = params["color"]["r"], params["color"]["g"], params["color"]["b"]
        self.SetPointsColor(id, red, green, blue)

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["size"]["rpc"])
    def setMeshPointsSize(self, params):
        print(self.mesh_points_prefix + self.mesh_points_schemas_dict["size"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_points_schemas_dict["size"])
        id = str(params["id"])
        size = float(params["size"])
        self.SetPointsSize(id, size)

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["vertex_attribute"]["rpc"])
    def setMeshPointsVertexAttribute(self, params):
        print(self.mesh_points_prefix + self.mesh_points_schemas_dict["vertex_attribute"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_points_schemas_dict["vertex_attribute"])
        id = str(params["id"])
        name = str(params["name"])
        self.displayAttributeOnVertices(id, name)
    