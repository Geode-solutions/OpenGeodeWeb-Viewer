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


class VtkMeshCellsAttributeVertexView(VtkMeshView):
    mesh_cells_attribute_vertex_prefix = (
        "opengeodeweb_viewer.mesh.cells.attribute.vertex."
    )
    mesh_cells_attribute_vertex_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(
        mesh_cells_attribute_vertex_prefix
        + mesh_cells_attribute_vertex_schemas_dict["name"]["rpc"]
    )
    def setMeshCellsVertexName(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_cells_attribute_vertex_schemas_dict["name"],
            self.mesh_cells_attribute_vertex_prefix,
        )
        params = schemas.Name.from_dict(rpc_params)
        self.displayAttributeOnVertices(params.id, params.name)


    @exportRpc(
        mesh_cells_attribute_vertex_prefix
        + mesh_cells_attribute_vertex_schemas_dict["color_map"]["rpc"]
    )
    def setMeshCellsVertexColorMap(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_cells_attribute_vertex_schemas_dict["color_map"],
            self.mesh_cells_attribute_vertex_prefix,
        )
        params = schemas.ColorMap.from_dict(rpc_params)
        self.setupColorMap(params.id, params.points, params.minimum, params.maximum)
