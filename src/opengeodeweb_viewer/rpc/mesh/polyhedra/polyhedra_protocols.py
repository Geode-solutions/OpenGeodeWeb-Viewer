# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkMeshPolyhedraView(VtkMeshView):
    mesh_polyhedra_prefix = "opengeodeweb_viewer.mesh.polyhedra."
    mesh_polyhedra_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_polyhedra_prefix, schemas.visibility_route)
    def setMeshPolyhedraVisibility(
        self, params: schemas.Visibility
    ) -> schemas.VisibilityResponse:
        self.SetVisibility(params.id, params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(mesh_polyhedra_prefix, schemas.color_route)
    def setMeshPolyhedraColor(self, params: schemas.Color) -> schemas.ColorResponse:
        color = params.color
        self.SetColor(params.id, color.red, color.green, color.blue, color.alpha)
        return schemas.ColorResponse()
