# Standard library imports
import os

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.typed_rpc import typed_rpc
from . import schemas


class VtkMeshPointsView(VtkMeshView):
    mesh_points_prefix = "opengeodeweb_viewer.mesh.points."
    mesh_points_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_points_prefix, schemas.visibility_route)
    def setMeshPointsVisibility(
        self, params: schemas.Visibility
    ) -> schemas.VisibilityResponse:
        self.SetPointsVisibility(params.id, params.visibility)
        return schemas.VisibilityResponse(id=params.id, visibility=params.visibility)

    @typed_rpc(mesh_points_prefix, schemas.color_route)
    def setMeshPointsColor(self, params: schemas.Color) -> schemas.ColorResponse:
        color = params.color
        self.SetPointsColor(params.id, color.red, color.green, color.blue, color.alpha)
        return schemas.ColorResponse()

    @typed_rpc(mesh_points_prefix, schemas.size_route)
    def setMeshPointsSize(self, params: schemas.Size) -> schemas.SizeResponse:
        self.SetPointsSize(params.id, params.size)
        return schemas.SizeResponse()
