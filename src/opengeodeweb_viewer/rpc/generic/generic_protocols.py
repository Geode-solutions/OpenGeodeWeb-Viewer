# Standard library imports
import json
import os

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.vtk_protocol import VtkView
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema

class VtkGenericView(VtkView):
    prefix = "opengeodeweb_viewer.generic."
    schemas_dict = get_schemas_dict(os.path.join(os.path.dirname(__file__), "schemas"))

    def __init__(self, mesh_protocols, model_protocols):
        super().__init__()
        self.mesh_protocols = mesh_protocols
        self.model_protocols = model_protocols
    
    @exportRpc(prefix + schemas_dict["register"]["rpc"])
    def register(self, params):
        print(self.schemas_dict["register"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.schemas_dict["register"])
        viewer_object = params["viewer_object"]
        params.pop('viewer_object', None)
        print(f"{params=}", flush=True)
        if viewer_object == "mesh":
            self.mesh_protocols.registerMesh(params)
        elif viewer_object == "model":
            self.model_protocols.registerModel(params)

    @exportRpc(prefix + schemas_dict["deregister"]["rpc"])
    def deregister(self, params):
        print(self.schemas_dict["deregister"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.schemas_dict["deregister"])
        viewer_object = params["viewer_object"]
        params.pop('viewer_object', None)
        if viewer_object == "mesh":
            self.mesh_protocols.deregisterMesh(params)
        elif viewer_object == "model":
            self.model_protocols.deregisterModel(params)


