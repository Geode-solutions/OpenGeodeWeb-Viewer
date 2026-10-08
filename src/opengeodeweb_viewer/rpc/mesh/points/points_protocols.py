# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkMeshPointsView(VtkMeshView):
    mesh_points_prefix = "opengeodeweb_viewer.mesh.points."
    mesh_points_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_points_prefix, schemas.visibility_route)
    def set_mesh_points_visibility(self, params: schemas.Visibility) -> schemas.VisibilityResponse:
        self.set_points_visibility(params.id, visibility=params.visibility)
        return schemas.VisibilityResponse(id=params.id, visibility=params.visibility)

    @typed_rpc(mesh_points_prefix, schemas.color_route)
    def set_mesh_points_color(self, params: schemas.Color) -> schemas.ColorResponse:
        color = params.color
        self.set_points_color(params.id, color)
        return schemas.ColorResponse()

    @typed_rpc(mesh_points_prefix, schemas.size_route)
    def set_mesh_points_size(self, params: schemas.Size) -> schemas.SizeResponse:
        self.set_points_size(params.id, params.size)
        return schemas.SizeResponse()
