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


class VtkMeshPolyhedraView(VtkMeshView):
    mesh_polyhedra_prefix = "opengeodeweb_viewer.mesh.polyhedra."
    mesh_polyhedra_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(mesh_polyhedra_prefix + mesh_polyhedra_schemas_dict["visibility"]["rpc"])
    def setMeshPolyhedraVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polyhedra_schemas_dict["visibility"],
            self.mesh_polyhedra_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetVisibility(params.id, params.visibility)

    @exportRpc(mesh_polyhedra_prefix + mesh_polyhedra_schemas_dict["color"]["rpc"])
    def setMeshPolyhedraColor(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polyhedra_schemas_dict["color"],
            self.mesh_polyhedra_prefix,
        )
        params = schemas.Color.from_dict(rpc_params)
        color = params.color
        self.SetColor(params.id, color.r, color.g, color.b)

    @exportRpc(
        mesh_polyhedra_prefix + mesh_polyhedra_schemas_dict["vertex_attribute"]["rpc"]
    )
    def setMeshPolyhedraVertexAttribute(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polyhedra_schemas_dict["vertex_attribute"],
            self.mesh_polyhedra_prefix,
        )
        params = schemas.VertexAttribute.from_dict(rpc_params)
        self.displayAttributeOnVertices(params.id, params.name)

    @exportRpc(
        mesh_polyhedra_prefix
        + mesh_polyhedra_schemas_dict["polyhedron_attribute"]["rpc"]
    )
    def setMeshPolyhedraPolyhedronAttribute(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polyhedra_schemas_dict["polyhedron_attribute"],
            self.mesh_polyhedra_prefix,
        )
        params = schemas.PolyhedronAttribute.from_dict(rpc_params)
        self.displayAttributeOnCells(params.id, params.name)

    @exportRpc(
        mesh_polyhedra_prefix
        + mesh_polyhedra_schemas_dict["vertex_scalar_range"]["rpc"]
    )
    def setMeshPolyhedraVertexScalarRange(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polyhedra_schemas_dict["vertex_scalar_range"],
            self.mesh_polyhedra_prefix,
        )
        params = schemas.VertexScalarRange.from_dict(rpc_params)
        self.displayScalarRange(params.id, params.minimum, params.maximum)

    @exportRpc(
        mesh_polyhedra_prefix
        + mesh_polyhedra_schemas_dict["polyhedron_scalar_range"]["rpc"]
    )
    def setMeshPolyhedraPolyhedronScalarRange(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polyhedra_schemas_dict["polyhedron_scalar_range"],
            self.mesh_polyhedra_prefix,
        )
        params = schemas.PolyhedronScalarRange.from_dict(rpc_params)
        self.displayScalarRange(params.id, params.minimum, params.maximum)
