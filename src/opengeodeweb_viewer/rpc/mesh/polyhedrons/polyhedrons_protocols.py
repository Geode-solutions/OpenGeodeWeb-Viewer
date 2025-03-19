# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView


class VtkMeshPolyhedronsView(VtkMeshView):
    mesh_polyhedrons_prefix = "opengeodeweb_viewer.mesh.polyhedrons."
    mesh_polyhedrons_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(
        mesh_polyhedrons_prefix + mesh_polyhedrons_schemas_dict["visibility"]["rpc"]
    )
    def setMeshPolyhedronsVisibility(self, params):
        validate_schema(
            params,
            self.mesh_polyhedrons_schemas_dict["visibility"],
            self.mesh_polyhedrons_prefix,
        )
        id, visibility = params["id"], params["visibility"]
        self.SetVisibility(id, visibility)

    @exportRpc(mesh_polyhedrons_prefix + mesh_polyhedrons_schemas_dict["color"]["rpc"])
    def setMeshPolyhedronsColor(self, params):
        validate_schema(
            params,
            self.mesh_polyhedrons_schemas_dict["color"],
            self.mesh_polyhedrons_prefix,
        )
        id, red, green, blue = (
            params["id"],
            params["color"]["r"],
            params["color"]["g"],
            params["color"]["b"],
        )
        self.SetColor(id, red, green, blue)

    @exportRpc(
        mesh_polyhedrons_prefix
        + mesh_polyhedrons_schemas_dict["vertex_attribute"]["rpc"]
    )
    def setMeshPolyhedronsVertexAttribute(self, params):
        validate_schema(
            params,
            self.mesh_polyhedrons_schemas_dict["vertex_attribute"],
            self.mesh_polyhedrons_prefix,
        )
        id, name = params["id"], params["name"]
        self.displayAttributeOnVertices(id, name)

    @exportRpc(
        mesh_polyhedrons_prefix
        + mesh_polyhedrons_schemas_dict["polyhedron_attribute"]["rpc"]
    )
    def setMeshPolyhedronsPolyhedronAttribute(self, params):
        validate_schema(
            params,
            self.mesh_polyhedrons_schemas_dict["polyhedron_attribute"],
            self.mesh_polyhedrons_prefix,
        )
        id, name = params["id"], params["name"]
        self.displayAttributeOnCells(id, name)
