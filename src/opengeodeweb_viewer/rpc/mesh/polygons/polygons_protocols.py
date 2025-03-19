# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView


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
        id, visibility = params["id"], params["visibility"]
        self.SetVisibility(id, visibility)

    @exportRpc(mesh_polygons_prefix + mesh_polygons_schemas_dict["color"]["rpc"])
    def setMeshPolygonsColor(self, params):
        validate_schema(
            params,
            self.mesh_polygons_schemas_dict["color"],
            self.mesh_polygons_prefix,
        )
        id, red, green, blue = (
            params["id"],
            params["color"]["r"],
            params["color"]["g"],
            params["color"]["b"],
        )
        self.SetColor(id, red, green, blue)

    @exportRpc(
        mesh_polygons_prefix + mesh_polygons_schemas_dict["vertex_attribute"]["rpc"]
    )
    def setMeshPolygonsVertexAttribute(self, params):
        validate_schema(
            params,
            self.mesh_polygons_schemas_dict["vertex_attribute"],
            self.mesh_polygons_prefix,
        )
        id, name = params["id"], params["name"]
        self.displayAttributeOnVertices(id, name)

    @exportRpc(
        mesh_polygons_prefix + mesh_polygons_schemas_dict["polygon_attribute"]["rpc"]
    )
    def setMeshPolygonsPolygonAttribute(self, params):
        validate_schema(
            params,
            self.mesh_polygons_schemas_dict["polygon_attribute"],
            self.mesh_polygons_prefix,
        )
        id, name = params["id"], params["name"]
        self.displayAttributeOnCells(id, name)
