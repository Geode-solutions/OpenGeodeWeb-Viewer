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


class VtkMeshPolygonsView(VtkMeshView):
    mesh_polygons_prefix = "opengeodeweb_viewer.mesh.polygons."
    mesh_polygons_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(mesh_polygons_prefix + mesh_polygons_schemas_dict["visibility"]["rpc"])
    def setMeshPolygonsVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polygons_schemas_dict["visibility"],
            self.mesh_polygons_prefix,
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetVisibility(params.id, params.visibility)

    @exportRpc(mesh_polygons_prefix + mesh_polygons_schemas_dict["color"]["rpc"])
    def setMeshPolygonsColor(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polygons_schemas_dict["color"],
            self.mesh_polygons_prefix,
        )
        params = schemas.Color.from_dict(rpc_params)
        color = params.color
        self.SetColor(params.id, color.r, color.g, color.b)

    @exportRpc(
        mesh_polygons_prefix + mesh_polygons_schemas_dict["vertex_attribute"]["rpc"]
    )
    def setMeshPolygonsVertexAttribute(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polygons_schemas_dict["vertex_attribute"],
            self.mesh_polygons_prefix,
        )
        params = schemas.VertexAttribute.from_dict(rpc_params)
        self.displayAttributeOnVertices(params.id, params.name)

    @exportRpc(
        mesh_polygons_prefix + mesh_polygons_schemas_dict["polygon_attribute"]["rpc"]
    )
    def setMeshPolygonsPolygonAttribute(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polygons_schemas_dict["polygon_attribute"],
            self.mesh_polygons_prefix,
        )
        params = schemas.PolygonAttribute.from_dict(rpc_params)
        self.displayAttributeOnCells(params.id, params.name)

    @exportRpc(
        mesh_polygons_prefix + mesh_polygons_schemas_dict["vertex_scalar_range"]["rpc"]
    )
    def setMeshPolygonsVertexScalarRange(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polygons_schemas_dict["vertex_scalar_range"],
            self.mesh_polygons_prefix,
        )
        params = schemas.VertexScalarRange.from_dict(rpc_params)
        self.displayScalarRange(params.id, params.minimum, params.maximum)

    @exportRpc(
        mesh_polygons_prefix + mesh_polygons_schemas_dict["polygon_scalar_range"]["rpc"]
    )
    def setMeshPolygonsPolygonScalarRange(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.mesh_polygons_schemas_dict["polygon_scalar_range"],
            self.mesh_polygons_prefix,
        )
        params = schemas.PolygonScalarRange.from_dict(rpc_params)
        self.displayScalarRange(params.id, params.minimum, params.maximum)
