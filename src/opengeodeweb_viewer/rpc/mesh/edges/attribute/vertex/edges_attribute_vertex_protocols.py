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


class VtkMeshEdgesAttributeVertexView(VtkMeshView):
    mesh_edges_prefix = "opengeodeweb_viewer.mesh.edges."
    mesh_edges_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["attribute"]["rpc"])
    def setMeshEdgesVertexAttribute(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_edges_schemas_dict["attribute"],
            self.mesh_edges_prefix,
        )
        params = schemas.Attribute.from_dict(rpc_params)
        self.displayAttributeOnVertices(params.id, params.name)

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["scalar_range"]["rpc"])
    def setMeshEdgesVertexScalarRange(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_edges_schemas_dict["scalar_range"],
            self.mesh_edges_prefix,
        )
        params = schemas.ScalarRange.from_dict(rpc_params)
        self.displayScalarRange(params.id, params.minimum, params.maximum)

    @exportRpc(mesh_edges_prefix + mesh_edges_schemas_dict["color_map"]["rpc"])
    def setMeshEdgesVertexColorMap(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_edges_schemas_dict["color_map"],
            self.mesh_edges_prefix,
        )
        params = schemas.ColorMap.from_dict(rpc_params)
        self.setupColorMap(params.id, params.points, params.minimum, params.maximum)
