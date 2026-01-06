# Standard library imports
import os

# Third party imports
from vtkmodules.web import protocols as vtk_protocols
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.vtk_protocol import VtkView
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.utils_functions import (
    validate_schema,
    RpcParams,
)
from . import schemas


class VtkGenericView(VtkView):
    generic_prefix = "opengeodeweb_viewer.generic."
    generic_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(
        self, mesh_protocols: VtkMeshView, model_protocols: VtkModelView
    ) -> None:
        super().__init__()
        self.mesh_protocols = mesh_protocols
        self.model_protocols = model_protocols

    @exportRpc(generic_prefix + generic_schemas_dict["register"]["rpc"])
    def register(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.generic_schemas_dict["register"], self.generic_prefix
        )
        params = schemas.Register.from_dict(rpc_params)
        data_id = params.id
        specific_params = {"id": data_id}
        data = self.get_data(data_id)
        viewer_object = str(data["viewer_object"])
        if viewer_object == "mesh":
            self.mesh_protocols.registerMesh(specific_params)
        elif viewer_object == "model":
            self.model_protocols.registerModel(specific_params)

    @exportRpc(generic_prefix + generic_schemas_dict["deregister"]["rpc"])
    def deregister(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.generic_schemas_dict["deregister"], self.generic_prefix
        )
        params = schemas.Deregister.from_dict(rpc_params)
        data_id = params.id
        specific_params = {"id": data_id}
        data = self.get_data(data_id)
        viewer_object = str(data["viewer_object"])
        if viewer_object == "mesh":
            self.mesh_protocols.deregisterMesh(specific_params)
        elif viewer_object == "model":
            self.model_protocols.deregisterModel(specific_params)
