# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkMeshEdgesView(VtkMeshView):
    mesh_edges_prefix = "opengeodeweb_viewer.mesh.edges."
    mesh_edges_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_edges_prefix, schemas.visibility_route)
    def set_mesh_edges_visibility(
        self, params: schemas.Visibility
    ) -> schemas.VisibilityResponse:
        self.set_edges_visibility(params.id, visibility=params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(mesh_edges_prefix, schemas.color_route)
    def set_mesh_edges_color(self, params: schemas.Color) -> schemas.ColorResponse:
        color = params.color
        self.set_edges_color(params.id, color)
        return schemas.ColorResponse()

    @typed_rpc(mesh_edges_prefix, schemas.width_route)
    def set_mesh_edges_width(self, params: schemas.Width) -> schemas.WidthResponse:
        self.set_edges_width(params.id, params.width)
        return schemas.WidthResponse()
