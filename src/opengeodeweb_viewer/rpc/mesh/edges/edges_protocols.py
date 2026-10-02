# Standard library imports
import os

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.typed_rpc import typed_rpc
from . import schemas


class VtkMeshEdgesView(VtkMeshView):
    mesh_edges_prefix = "opengeodeweb_viewer.mesh.edges."
    mesh_edges_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_edges_prefix, schemas.visibility_route)
    def setMeshEdgesVisibility(
        self, params: schemas.Visibility
    ) -> schemas.VisibilityResponse:
        self.SetEdgesVisibility(params.id, params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(mesh_edges_prefix, schemas.color_route)
    def setMeshEdgesColor(self, params: schemas.Color) -> schemas.ColorResponse:
        color = params.color
        self.SetEdgesColor(params.id, color.red, color.green, color.blue, color.alpha)
        return schemas.ColorResponse()

    @typed_rpc(mesh_edges_prefix, schemas.width_route)
    def setMeshEdgesWidth(self, params: schemas.Width) -> schemas.WidthResponse:
        self.SetEdgesWidth(params.id, params.width)
        return schemas.WidthResponse()
