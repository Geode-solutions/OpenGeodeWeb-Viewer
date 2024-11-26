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

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
schemas_dict = get_schemas_dict(schemas_dir)
prefix = "opengeodeweb_viewer."

class VtkGenericView(VtkView):
    def __init__(self):
        super().__init__()
        self.prefix = prefix
        self.schemas_dict = schemas_dict
    
    @exportRpc(prefix + schemas_dict["register"]["rpc"])
    def register(self, params):

        print(f"{schemas_dict=}", flush=True)
        print(f"{params=}", flush=True)
        validate_schema(params, schemas_dict["register"])
        viewer_object = params["viewer_object"]
        params.pop('viewer_object', None)
        print(f"{params=}", flush=True)
        if viewer_object == "mesh":
            print(f"MESH", flush=True)
            class_ = VtkMeshView()
            class_.registerMesh(params)
        elif viewer_object == "model":
            print(f"MODEL", flush=True)
            class_ = VtkModelView()
            class_.registerModel(params)

    @exportRpc(prefix + schemas_dict["deregister"]["rpc"])
    def deregister(self, params):
        validate_schema(params, schemas_dict["deregister"])
        viewer_object = params["viewer_object"]
        params.pop('viewer_object', None)
        if viewer_object == "mesh":
            VtkMeshView.registerMesh(self, params)
        elif viewer_object == "model":
            VtkModelView.registerModel(self, params)




