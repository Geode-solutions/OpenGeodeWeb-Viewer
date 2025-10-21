# Standard library imports
import os

# Third party imports
from vtk.web import protocols as vtk_protocols
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.vtk_protocol import VtkView
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from . import schemas


class VtkGenericView(VtkView):
    prefix = "opengeodeweb_viewer.generic."
    schemas_dict = get_schemas_dict(os.path.join(os.path.dirname(__file__), "schemas"))

    def __init__(
        self, mesh_protocols: VtkMeshView, model_protocols: VtkModelView
    ) -> None:
        super().__init__()
        self.mesh_protocols = mesh_protocols
        self.model_protocols = model_protocols

    @exportRpc(prefix + schemas_dict["register"]["rpc"])
    def register(self, params):
        validate_schema(params, self.schemas_dict["register"], self.prefix)
        params = schemas.Register.from_dict(params)
        data_id = params.id
        specific_params = {"id": data_id}
        data = self.get_data(data_id)
        viewer_object = str(data["viewer_object"])
        if viewer_object == "mesh":
            self.mesh_protocols.registerMesh(specific_params)
        elif viewer_object == "model":
            self.model_protocols.registerModel(specific_params)

    @exportRpc(prefix + schemas_dict["deregister"]["rpc"])
    def deregister(self, params):
        validate_schema(params, self.schemas_dict["deregister"], self.prefix)
        params = schemas.Deregister.from_dict(params)
        data_id = params.id
        specific_params = {"id": data_id}
        data = self.get_data(data_id)
        viewer_object = str(data["viewer_object"])
        if viewer_object == "mesh":
            self.mesh_protocols.deregisterMesh(specific_params)
        elif viewer_object == "model":
            self.model_protocols.deregisterModel(specific_params)
