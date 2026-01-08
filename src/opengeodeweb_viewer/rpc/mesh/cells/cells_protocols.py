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


class VtkMeshCellsView(VtkMeshView):
    mesh_cells_prefix = "opengeodeweb_viewer.mesh.cells."
    mesh_cells_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(mesh_cells_prefix + mesh_cells_schemas_dict["visibility"]["rpc"])
    def setMeshCellsVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_cells_schemas_dict["visibility"],
            self.mesh_cells_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetVisibility(params.id, params.visibility)

    @exportRpc(mesh_cells_prefix + mesh_cells_schemas_dict["color"]["rpc"])
    def setMeshCellsColor(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_cells_schemas_dict["color"],
            self.mesh_cells_prefix,
        )
        params = schemas.Color.from_dict(rpc_params)
        color = params.color
        self.SetColor(params.id, color.r, color.g, color.b)

    @exportRpc(mesh_cells_prefix + mesh_cells_schemas_dict["vertex_attribute"]["rpc"])
    def setMeshCellsVertexAttribute(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_cells_schemas_dict["vertex_attribute"],
            self.mesh_cells_prefix,
        )
        params = schemas.VertexAttribute.from_dict(rpc_params)
        self.displayAttributeOnVertices(params.id, params.name)

    @exportRpc(mesh_cells_prefix + mesh_cells_schemas_dict["cell_attribute"]["rpc"])
    def setMeshCellsCellAttribute(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_cells_schemas_dict["cell_attribute"],
            self.mesh_cells_prefix,
        )
        params = schemas.CellAttribute.from_dict(rpc_params)
        self.displayAttributeOnCells(params.id, params.name)

    @exportRpc(
        mesh_cells_prefix + mesh_cells_schemas_dict["vertex_scalar_range"]["rpc"]
    )
    def setMeshCellsVertexScalarRange(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_cells_schemas_dict["vertex_scalar_range"],
            self.mesh_cells_prefix,
        )
        params = schemas.VertexScalarRange.from_dict(rpc_params)
        self.displayScalarRange(params.id, params.minimum, params.maximum)

    @exportRpc(mesh_cells_prefix + mesh_cells_schemas_dict["cell_scalar_range"]["rpc"])
    def setMeshCellsCellScalarRange(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_cells_schemas_dict["cell_scalar_range"],
            self.mesh_cells_prefix,
        )
        params = schemas.CellScalarRange.from_dict(rpc_params)
        self.displayScalarRange(params.id, params.minimum, params.maximum)
