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
            rpc_params,
            self.mesh_edges_schemas_dict["visibility"],
            self.mesh_edges_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetEdgesVisibility(params.id, params.visibility)

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["color"]["rpc"])
    def setMeshEdgesColor(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.mesh_edges_schemas_dict["color"], self.mesh_edges_prefix
        )
        params = schemas.Color.from_dict(rpc_params)
        color = params.color
        self.SetEdgesColor(params.id, color.r, color.g, color.b)

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["width"]["rpc"])
    def setMeshEdgesWidth(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.mesh_edges_schemas_dict["width"], self.mesh_edges_prefix
        )
        params = schemas.Width.from_dict(rpc_params)
        self.SetEdgesWidth(params.id, params.width)

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["vertex_attribute"]["rpc"])
    def setMeshEdgesVertexAttribute(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_edges_schemas_dict["vertex_attribute"],
            self.mesh_edges_prefix,
        )
        params = schemas.VertexAttribute.from_dict(rpc_params)
        self.displayAttributeOnVertices(params.id, params.name)

    @exportRpc(
        mesh_edges_prefix + mesh_edges_schemas_dict["vertex_scalar_range"]["rpc"]
    )
    def setMeshEdgesVertexScalarRange(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_edges_schemas_dict["vertex_scalar_range"],
            self.mesh_edges_prefix,
        )
        params = schemas.VertexScalarRange.from_dict(rpc_params)
        self.displayScalarRange(params.id, params.minimum, params.maximum)
