# Standard library imports
from pathlib import Path

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas


class VtkMeshCellsView(VtkMeshView):
    mesh_cells_prefix = "opengeodeweb_viewer.mesh.cells."
    mesh_cells_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_cells_prefix, schemas.visibility_route)
    def set_mesh_cells_visibility(
        self, params: schemas.Visibility
    ) -> schemas.VisibilityResponse:
        self.set_visibility(params.id, visibility=params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(mesh_cells_prefix, schemas.color_route)
    def set_mesh_cells_color(self, params: schemas.Color) -> schemas.ColorResponse:
        color = params.color
        self.set_color(params.id, color)
        return schemas.ColorResponse()
