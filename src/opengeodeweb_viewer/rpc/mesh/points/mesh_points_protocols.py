# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import (
    validate_schema,
    RpcParams,
)
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from . import schemas


class VtkMeshPointsView(VtkMeshView):
    mesh_points_prefix = "opengeodeweb_viewer.mesh.points."
    mesh_points_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["visibility"]["rpc"])
    def setMeshPointsVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_points_schemas_dict["visibility"],
            self.mesh_points_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetPointsVisibility(params.id, params.visibility)

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["color"]["rpc"])
    def setMeshPointsColor(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.mesh_points_schemas_dict["color"], self.mesh_points_prefix
        )
        params = schemas.Color.from_dict(rpc_params)
        color = params.color
        self.SetPointsColor(params.id, color.r, color.g, color.b)

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["size"]["rpc"])
    def setMeshPointsSize(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.mesh_points_schemas_dict["size"], self.mesh_points_prefix
        )
        params = schemas.Size.from_dict(rpc_params)
        self.SetPointsSize(params.id, params.size)

    @exportRpc(mesh_points_prefix + mesh_points_schemas_dict["vertex_attribute"]["rpc"])
    def setMeshPointsVertexAttribute(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_points_schemas_dict["vertex_attribute"],
            self.mesh_points_prefix,
        )
        params = schemas.VertexAttribute.from_dict(rpc_params)
        self.displayAttributeOnVertices(params.id, params.name)

    @exportRpc(
        mesh_points_prefix + mesh_points_schemas_dict["vertex_scalar_range"]["rpc"]
    )
    def setMeshPointsVertexScalarRange(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_points_schemas_dict["vertex_scalar_range"],
            self.mesh_points_prefix,
        )
        params = schemas.VertexScalarRange.from_dict(rpc_params)
        self.displayScalarRange(params.id, params.minimum, params.maximum)
