# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from . import schemas


class VtkMeshPolygonsView(VtkMeshView):
    mesh_polygons_prefix = "opengeodeweb_viewer.mesh.polygons."
    mesh_polygons_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(mesh_polygons_prefix + mesh_polygons_schemas_dict["visibility"]["rpc"])
    def setMeshPolygonsVisibility(self, params):
        validate_schema(
            params,
            self.mesh_polygons_schemas_dict["visibility"],
            self.mesh_polygons_prefix,
        )
        params = schemas.Visibility.from_dict(params)
        self.SetVisibility(params.id, params.visibility)

    @exportRpc(mesh_polygons_prefix + mesh_polygons_schemas_dict["color"]["rpc"])
    def setMeshPolygonsColor(self, params):
        validate_schema(
            params,
            self.mesh_polygons_schemas_dict["color"],
            self.mesh_polygons_prefix,
        )
        params = schemas.Color.from_dict(params)
        color = params.color
        self.SetColor(params.id, color.r, color.g, color.b)

    @exportRpc(
        mesh_polygons_prefix + mesh_polygons_schemas_dict["vertex_attribute"]["rpc"]
    )
    def setMeshPolygonsVertexAttribute(self, params):
        validate_schema(
            params,
            self.mesh_polygons_schemas_dict["vertex_attribute"],
            self.mesh_polygons_prefix,
        )
        params = schemas.Color.from_dict(params)
        self.displayAttributeOnVertices(params.id, params.name)

    @exportRpc(
        mesh_polygons_prefix + mesh_polygons_schemas_dict["polygon_attribute"]["rpc"]
    )
    def setMeshPolygonsPolygonAttribute(self, params):
        validate_schema(
            params,
            self.mesh_polygons_schemas_dict["polygon_attribute"],
            self.mesh_polygons_prefix,
        )
        params = schemas.Color.from_dict(params)
        self.displayAttributeOnCells(params.id, params.name)
