# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import (
    get_schemas_dict,
    validate_schema,
    RpcParams,
    RpcParamsWithColor,
)
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView


class VtkMeshPointsView(VtkMeshView):
    mesh_points_prefix = "opengeodeweb_viewer.mesh.points."
    mesh_points_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["visibility"]["rpc"])
    def setMeshPointsVisibility(self, params: RpcParams) -> None:
        validate_schema(
            params, self.mesh_points_schemas_dict["visibility"], self.mesh_points_prefix
        )
        id, visibility = params["id"], params["visibility"]
        self.SetPointsVisibility(id, visibility)

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["color"]["rpc"])
    def setMeshPointsColor(self, params: RpcParamsWithColor) -> None:
        validate_schema(
            params, self.mesh_points_schemas_dict["color"], self.mesh_points_prefix
        )
        id, red, green, blue = (
            params["id"],
            params["color"]["r"],
            params["color"]["g"],
            params["color"]["b"],
        )
        self.SetPointsColor(id, red, green, blue)

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["size"]["rpc"])
    def setMeshPointsSize(self, params: RpcParams) -> None:
        validate_schema(
            params, self.mesh_points_schemas_dict["size"], self.mesh_points_prefix
        )
        id, size = params["id"], params["size"]
        self.SetPointsSize(id, size)

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["vertex_attribute"]["rpc"])
    def setMeshPointsVertexAttribute(self, params: RpcParams) -> None:
        validate_schema(
            params,
            self.mesh_points_schemas_dict["vertex_attribute"],
            self.mesh_points_prefix,
        )
        id, name = params["id"], params["name"]
        self.displayAttributeOnVertices(id, name)
