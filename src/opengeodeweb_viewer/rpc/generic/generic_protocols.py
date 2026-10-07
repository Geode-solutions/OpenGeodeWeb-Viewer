# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.typed_rpc import typed_rpc

# Local application imports
from opengeodeweb_viewer.vtk_protocol import VtkView

from . import schemas


class VtkGenericView(VtkView):
    generic_prefix = "opengeodeweb_viewer.generic."
    generic_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(
        self, mesh_protocols: VtkMeshView, model_protocols: VtkModelView
    ) -> None:
        super().__init__()
        self.mesh_protocols = mesh_protocols
        self.model_protocols = model_protocols

    @typed_rpc(generic_prefix, schemas.register_route)
    def register(self, params: schemas.Register) -> schemas.RegisterResponse:
        data_id = params.id
        specific_params = {"id": data_id, "name": params.name}
        viewer_object = self.get_viewer_data(data_id).viewer_object
        if viewer_object == "mesh":
            self.mesh_protocols.registerMesh(specific_params)
        elif viewer_object == "model":
            self.model_protocols.registerModel(specific_params)
        return schemas.RegisterResponse()

    @typed_rpc(generic_prefix, schemas.deregister_route)
    def deregister(self, params: schemas.Deregister) -> schemas.DeregisterResponse:
        data_id = params.id
        specific_params = {"id": data_id}
        viewer_object = self.get_viewer_data(data_id).viewer_object
        if viewer_object == "mesh":
            self.mesh_protocols.deregisterMesh(specific_params)
        elif viewer_object == "model":
            self.model_protocols.deregisterModel(specific_params)
        return schemas.DeregisterResponse()
