# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from . import schemas


class VtkMeshEdgesView(VtkMeshView):
    mesh_edges_prefix = "opengeodeweb_viewer.mesh.edges."
    mesh_edges_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["visibility"]["rpc"])
    def setMeshEdgesVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            params, self.mesh_edges_schemas_dict["visibility"], self.mesh_edges_prefix
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetEdgesVisibility(params.id, params.visibility)

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["color"]["rpc"])
    def setMeshEdgesColor(self, rpc_params: RpcParams) -> None:
        validate_schema(
            params, self.mesh_edges_schemas_dict["color"], self.mesh_edges_prefix
        )
        params = schemas.Color.from_dict(rpc_params)
        color = params.color
        self.SetEdgesColor(params.id, color.r, color.g, color.b)

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["width"]["rpc"])
    def setMeshEdgesWidth(self, rpc_params: RpcParams) -> None:
        validate_schema(
            params, self.mesh_edges_schemas_dict["width"], self.mesh_edges_prefix
        )
        params = schemas.Color.from_dict(rpc_params)
        self.SetEdgesWidth(params.id, params.width)
