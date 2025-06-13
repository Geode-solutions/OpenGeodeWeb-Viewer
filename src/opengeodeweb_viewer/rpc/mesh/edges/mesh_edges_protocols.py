# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView


class VtkMeshEdgesView(VtkMeshView):
    mesh_edges_prefix = "opengeodeweb_viewer.mesh.edges."
    mesh_edges_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["visibility"]["rpc"])
    def setMeshEdgesVisibility(self, params):
        validate_schema(
            params, self.mesh_edges_schemas_dict["visibility"], self.mesh_edges_prefix
        )
        id, visibility = params["id"], params["visibility"]
        self.SetEdgesVisibility(id, visibility)

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["color"]["rpc"])
    def setMeshEdgesColor(self, params):
        validate_schema(
            params, self.mesh_edges_schemas_dict["color"], self.mesh_edges_prefix
        )
        id, red, green, blue = (
            params["id"],
            params["color"]["r"],
            params["color"]["g"],
            params["color"]["b"],
        )
        self.SetEdgesColor(id, red, green, blue)

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["width"]["rpc"])
    def setMeshEdgesWidth(self, params):
        validate_schema(
            params, self.mesh_edges_schemas_dict["width"], self.mesh_edges_prefix
        )
        id, size = params["id"], params["width"]
        self.SetEdgesWidth(id, width)
