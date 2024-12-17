# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView

class VtkMeshPolygonsView(VtkMeshView):
    prefix = "opengeodeweb_viewer.mesh.polygons."
    schemas_dict = get_schemas_dict(os.path.join(os.path.dirname(__file__), "schemas"))

    def __init__(self):
        super().__init__()

    @exportRpc(prefix + schemas_dict["visibility"]["rpc"])
    def setMeshPolygonsVisibility(self, params):
        print(self.schemas_dict["visibility"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.schemas_dict["visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        self.SetPolygonsVisibility(id, visibility)

    @exportRpc(prefix + schemas_dict["color"]["rpc"])
    def setMeshPolygonsColor(self, params):
        print(self.schemas_dict["color"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.schemas_dict["color"])
        id = params["id"]
        color = bool(params["color"])
        self.SetPolygonsColor(id, color)

    @exportRpc(prefix + schemas_dict["vertex_attribute"]["rpc"])
    def setMeshPolygonsVertexAttribute(self, params):
        print(self.schemas_dict["vertex_attribute"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.schemas_dict["vertex_attribute"])
        id = params["id"]
        name = str(params["name"])
        self.setMeshVertexAttribute(id, name)

    @exportRpc(prefix + schemas_dict["polygon_attribute"]["rpc"])
    def setMeshPolygonsPolygonAttribute(self, params):
        print(self.schemas_dict["polygon_attribute"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.schemas_dict["polygon_attribute"])
        id = params["id"]
        name = str(params["name"])
        self.setMeshPolygonAttribute(id, name)
